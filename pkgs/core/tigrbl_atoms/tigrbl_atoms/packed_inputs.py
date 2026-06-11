from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any
import datetime as _dt
import decimal as _dc
import uuid as _uuid
from urllib.parse import unquote_plus

PARAM_SOURCE_BODY = 1
PARAM_SOURCE_QUERY = 2
PARAM_SOURCE_PATH = 4
PARAM_SOURCE_HEADER = 8

DECODE_STRATEGY_GENERIC_HASHED = 0
DECODE_STRATEGY_BODY_ONLY_MAPPING = 1
DECODE_STRATEGY_BODY_ONLY_SINGLE_FIELD = 2

DECODER_NONE = 0
DECODER_STR = 1
DECODER_INT = 2
DECODER_FLOAT = 3
DECODER_BOOL = 4
DECODER_UUID = 5
DECODER_DECIMAL = 6
DECODER_DATETIME = 7
DECODER_DATE = 8
DECODER_TIME = 9

QUERY_VALUE_HAS_PLUS = 1
QUERY_VALUE_HAS_PERCENT = 2


def coerce_header_pairs(
    raw_scope: Mapping[str, Any] | None,
) -> tuple[tuple[bytes, bytes], ...]:
    if not isinstance(raw_scope, Mapping):
        return ()
    raw_headers = raw_scope.get("headers", ())
    out: list[tuple[bytes, bytes]] = []
    for key, value in raw_headers or ():
        if not isinstance(key, (bytes, bytearray)):
            continue
        if not isinstance(value, (bytes, bytearray)):
            continue
        out.append((bytes(key).lower(), bytes(value)))
    return tuple(out)


def content_type_from_raw_headers(raw_headers: tuple[tuple[bytes, bytes], ...]) -> str:
    for key, value in reversed(raw_headers):
        if key == b"content-type":
            return value.decode("latin-1").lower()
    return ""


def decode_scalar(value: Any, decoder_id: int) -> Any:
    if value is None or decoder_id == DECODER_NONE:
        return value
    if isinstance(value, bytes):
        raw_text = value.decode("utf-8")
    else:
        raw_text = value if isinstance(value, str) else str(value)
    text = raw_text.strip()
    if decoder_id == DECODER_STR:
        return raw_text if isinstance(value, str) else text
    if decoder_id == DECODER_INT:
        return int(text)
    if decoder_id == DECODER_FLOAT:
        return float(text)
    if decoder_id == DECODER_BOOL:
        lowered = text.lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
        return value
    if decoder_id == DECODER_UUID:
        return _uuid.UUID(text)
    if decoder_id == DECODER_DECIMAL:
        return _dc.Decimal(text)
    if decoder_id == DECODER_DATETIME:
        return _dt.datetime.fromisoformat(text)
    if decoder_id == DECODER_DATE:
        return _dt.date.fromisoformat(text)
    if decoder_id == DECODER_TIME:
        return _dt.time.fromisoformat(text)
    return value


def parse_query_spans(
    raw_query: bytes,
    *,
    name_hash: Callable[[str], int],
) -> tuple[tuple[int, int, int, int], ...]:
    if not raw_query:
        return ()
    out: list[tuple[int, int, int, int]] = []
    cursor = 0
    for chunk in raw_query.split(b"&"):
        chunk_start = cursor
        cursor += len(chunk) + 1
        if not chunk:
            continue
        raw_key, _, raw_value = chunk.partition(b"=")
        try:
            key = unquote_plus(raw_key.decode("latin-1"))
        except Exception:
            continue
        flags = 0
        if b"+" in raw_value:
            flags |= QUERY_VALUE_HAS_PLUS
        if b"%" in raw_value:
            flags |= QUERY_VALUE_HAS_PERCENT
        value_start = chunk_start + len(raw_key) + (1 if b"=" in chunk else 0)
        value_end = chunk_start + len(chunk)
        out.append((name_hash(key), value_start, value_end, flags))
    return tuple(out)


def decode_query_span_value(raw_query: bytes, start: int, end: int, flags: int) -> str:
    raw_value = raw_query[start:end]
    text = raw_value.decode("latin-1")
    if flags & (QUERY_VALUE_HAS_PLUS | QUERY_VALUE_HAS_PERCENT):
        return unquote_plus(text)
    return text


async def ensure_body_bytes(ctx: Any, hot: Any) -> bytes:
    if isinstance(hot.body_bytes, bytes):
        return hot.body_bytes
    body = getattr(ctx, "body", None)
    if isinstance(body, bytes):
        hot.body_bytes = body
        hot.body_view = memoryview(body)
        return body
    if isinstance(body, bytearray):
        hot.body_bytes = bytes(body)
        hot.body_view = memoryview(hot.body_bytes)
        return hot.body_bytes
    if isinstance(body, memoryview):
        hot.body_bytes = body.tobytes()
        hot.body_view = memoryview(hot.body_bytes)
        return hot.body_bytes
    if hot.scope_type != "http" or not callable(hot.raw_receive):
        hot.body_bytes = b""
        hot.body_view = memoryview(hot.body_bytes)
        return hot.body_bytes
    message = await hot.raw_receive()
    chunks: list[bytes] = []
    while isinstance(message, dict) and message.get("type") == "http.request":
        chunk = message.get("body", b"")
        if isinstance(chunk, (bytes, bytearray)):
            chunks.append(bytes(chunk))
        if not bool(message.get("more_body", False)):
            break
        message = await hot.raw_receive()
    hot.body_bytes = b"".join(chunks)
    hot.body_view = memoryview(hot.body_bytes)
    if hot.body_bytes:
        ctx.body = hot.body_bytes
    return hot.body_bytes


def body_hash_items(
    body: Any,
    *,
    name_hash: Callable[[str], int],
) -> Mapping[int, Any]:
    if not isinstance(body, Mapping):
        return {}
    out: dict[int, Any] = {}
    for key, value in body.items():
        if not isinstance(key, str):
            continue
        out[name_hash(key)] = value
    return out


def header_hash_pairs(
    raw_headers: tuple[tuple[bytes, bytes], ...],
    *,
    name_hash: Callable[[str], int],
) -> tuple[tuple[int, bytes], ...]:
    return tuple(
        (name_hash(key_bytes.decode("latin-1")), raw_value)
        for key_bytes, raw_value in raw_headers
    )


def path_hash_items(
    path_params: Mapping[str, Any] | None,
    *,
    name_hash: Callable[[str], int],
) -> Mapping[int, Any]:
    if not isinstance(path_params, Mapping):
        return {}
    out: dict[int, Any] = {}
    for key, value in path_params.items():
        out[name_hash(str(key))] = value
    return out


def lookup_query_value(
    raw_query: bytes,
    query_spans: tuple[tuple[int, int, int, int], ...],
    target_hash: int,
) -> tuple[bool, Any]:
    for item_hash, value_start, value_end, flags in query_spans:
        if int(item_hash) != int(target_hash):
            continue
        return True, decode_query_span_value(
            raw_query, int(value_start), int(value_end), int(flags)
        )
    return False, None


def lookup_hashed_mapping(
    items: Mapping[int, Any],
    target_hash: int,
) -> tuple[bool, Any]:
    if int(target_hash) in items:
        return True, items[int(target_hash)]
    return False, None


def lookup_hashed_pairs(
    items: tuple[tuple[int, bytes], ...],
    target_hash: int,
) -> tuple[bool, Any]:
    for item_hash, raw_value in items:
        if int(item_hash) == int(target_hash):
            return True, raw_value.decode("latin-1")
    return False, None


def compiled_lookup_name(field_name: str, field_meta: Any) -> str:
    if isinstance(field_meta, Mapping):
        alias_in = field_meta.get("alias_in")
        if alias_in:
            return str(alias_in)
    return field_name


def publish_compiled_slots(
    hot: Any,
    field_names: tuple[str, ...],
    field_index: Mapping[str, int],
    slot_values: list[Any],
    slot_present: bytearray,
) -> None:
    hot.slot_field_names = field_names
    hot.slot_field_index = field_index
    hot.slot_values = slot_values
    hot.slot_present = slot_present
    hot.in_values_view = None
    hot.route_payload = None
    hot.in_present_names = tuple(
        field_names[idx] for idx in range(len(field_names)) if slot_present[idx]
    )
    hot.assembled_slot_values = None
    hot.assembled_slot_present = None
    hot.virtual_slot_values = None
    hot.virtual_slot_present = None
    hot.assembled_values_view = None
    hot.virtual_in_view = None
    hot.absent_fields = ()
    hot.used_default_factory = ()
    hot.compiled_in_invalid = None
    hot.compiled_in_errors = None
    hot.compiled_in_coerced = ()
    hot.compiled_input_ready = True
    hot.lazy_published = True
