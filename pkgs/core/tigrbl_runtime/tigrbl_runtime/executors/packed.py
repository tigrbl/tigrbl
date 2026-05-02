from __future__ import annotations

import asyncio
import inspect
import json
import uuid as _uuid
import decimal as _dc
import datetime as _dt
from importlib import import_module
from typing import Any, ClassVar, Mapping
from operator import attrgetter
from types import SimpleNamespace
from urllib.parse import unquote_plus

from tigrbl_atoms.types import build_error_ctx, error_phase_for, select_error_edge
from tigrbl_kernel.models import KernelPlan, OpKey, PackedKernel
from tigrbl_typing.phases import normalize_phase
from tigrbl_atoms._request import Request

from .base import ExecutorBase
from .types import HotCtx, _Ctx

_HOT_RUNNER_GENERIC = 0
_HOT_RUNNER_LINEAR_DIRECT = 1
_HOT_RUNNER_COMPILED_PARAM = 2
_DIRECT_INVOKE_STEP = 0
_DIRECT_INVOKE_RUN = 1
_DIRECT_INVOKE_RUN_WITH_NONE = 2
_DIRECT_INVOKE_RUN_WITH_DEP = 3
_TRANSPORT_KIND_GENERIC = 0
_TRANSPORT_KIND_REST = 1
_TRANSPORT_KIND_JSONRPC = 2
_TRANSPORT_KIND_CHANNEL = 3
_PARAM_SOURCE_BODY = 1
_PARAM_SOURCE_QUERY = 2
_PARAM_SOURCE_PATH = 4
_PARAM_SOURCE_HEADER = 8
_DECODER_NONE = 0
_DECODER_STR = 1
_DECODER_INT = 2
_DECODER_FLOAT = 3
_DECODER_BOOL = 4
_DECODER_UUID = 5
_DECODER_DECIMAL = 6
_DECODER_DATETIME = 7
_DECODER_DATE = 8
_DECODER_TIME = 9


class PackedPlanExecutor(ExecutorBase):
    """Executes packed kernel plans via kernel-attached packed execution hooks."""

    name: ClassVar[str] = "packed"
    _PHASE_EXECUTION_ORDER: ClassVar[tuple[str, ...]] = (
        "INGRESS_BEGIN",
        "INGRESS_PARSE",
        "INGRESS_DISPATCH",
        "PRE_TX_BEGIN",
        "START_TX",
        "PRE_HANDLER",
        "HANDLER",
        "POST_HANDLER",
        "PRE_COMMIT",
        "TX_COMMIT",
        "POST_COMMIT",
        "POST_RESPONSE",
        "EGRESS_SHAPE",
        "EGRESS_FINALIZE",
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._program_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], tuple[int, ...]]
        ] = {}
        self._request_program_cache: dict[tuple[int, str, str], int] = {}
        self._templated_route_cache: dict[int, tuple[tuple[str, Any, int], ...]] = {}
        self._opview_cache: dict[tuple[int, int], Any] = {}
        self._segment_steps_cache: dict[int, tuple[tuple[int, ...], ...]] = {}
        self._segment_runners_cache: dict[int, tuple[Any, ...]] = {}
        self._program_error_segments_cache: dict[
            tuple[int, int], tuple[tuple[int, ...], Mapping[str, tuple[int, ...]]]
        ] = {}
        self._program_runner_cache: dict[tuple[int, ...], Any] = {}
        self._program_runner_mode_cache: dict[tuple[int, int, int], Any] = {}
        self._db_acquire_cache: dict[tuple[int, int], Any] = {}
        self._model_row_serializer_cache: dict[type[Any], tuple[str, ...]] = {}

    @classmethod
    def _resolve_transport_senders(cls):
        from tigrbl_runtime.channel import channel_senders

        return channel_senders()

    @classmethod
    def _resolve_error_helpers(cls):
        from tigrbl_runtime.runtime.status import (
            StatusDetailError,
            create_standardized_error,
        )

        return StatusDetailError, create_standardized_error

    @staticmethod
    def _is_persistence_exception(exc: BaseException) -> bool:
        from tigrbl_typing.status.utils import is_persistence_exception

        return is_persistence_exception(exc)

    @staticmethod
    def _jsonrpc_error_payload(
        ctx: _Ctx,
        status_code: int,
        detail: Any,
        *,
        sanitize_detail: bool = False,
    ) -> dict[str, Any] | None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return None

        rpc_id = temp.get("jsonrpc_request_id")
        is_jsonrpc = "jsonrpc_request_id" in temp
        for section_key in ("route", "dispatch"):
            section = temp.get(section_key)
            if not isinstance(section, Mapping):
                continue
            for payload_key in ("rpc_envelope", "rpc"):
                payload = section.get(payload_key)
                if isinstance(payload, Mapping) and payload.get("jsonrpc") == "2.0":
                    is_jsonrpc = True
                    if rpc_id is None:
                        rpc_id = payload.get("id")

        if not is_jsonrpc:
            return None

        from tigrbl_typing.status.mappings import ERROR_MESSAGES, _HTTP_TO_RPC

        if sanitize_detail:
            status_code = 500
            detail = {"detail": "Internal error"}

        rpc_code = _HTTP_TO_RPC.get(int(status_code), -32603)
        data = dict(detail) if isinstance(detail, Mapping) else {"detail": detail}
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": rpc_code,
                "message": ERROR_MESSAGES.get(rpc_code, "Internal error"),
                "data": data,
            },
            "id": rpc_id,
        }

    @staticmethod
    def _hot_block_view(packed: PackedKernel) -> Mapping[str, Any]:
        view = getattr(packed, "hot_block_view", None)
        return view if isinstance(view, Mapping) else {}

    @classmethod
    def _hot_array(cls, packed: PackedKernel, key: str, fallback: tuple[Any, ...] | tuple[int, ...] | tuple[str, ...]) -> tuple[Any, ...]:
        view = cls._hot_block_view(packed)
        values = view.get(key)
        if isinstance(values, tuple):
            return values
        if isinstance(values, list):
            return tuple(values)
        return fallback

    @staticmethod
    def _stable_name_hash64(value: str, *, lowercase: bool = False) -> int:
        import hashlib

        normalized = value.lower() if lowercase else value
        digest = hashlib.blake2b(normalized.encode("utf-8"), digest_size=8).digest()
        return int.from_bytes(digest, "little", signed=False)

    @staticmethod
    def _coerce_header_pairs(
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

    @staticmethod
    def _content_type_from_raw_headers(raw_headers: tuple[tuple[bytes, bytes], ...]) -> str:
        for key, value in reversed(raw_headers):
            if key == b"content-type":
                return value.decode("latin-1").lower()
        return ""

    @staticmethod
    def _decode_scalar(value: Any, decoder_id: int) -> Any:
        if value is None or decoder_id == _DECODER_NONE:
            return value
        if isinstance(value, bytes):
            raw_text = value.decode("utf-8")
        else:
            raw_text = value if isinstance(value, str) else str(value)
        text = raw_text.strip()
        if decoder_id == _DECODER_STR:
            return raw_text if isinstance(value, str) else text
        if decoder_id == _DECODER_INT:
            return int(text)
        if decoder_id == _DECODER_FLOAT:
            return float(text)
        if decoder_id == _DECODER_BOOL:
            lowered = text.lower()
            if lowered in {"true", "1", "yes", "y", "on"}:
                return True
            if lowered in {"false", "0", "no", "n", "off"}:
                return False
            return value
        if decoder_id == _DECODER_UUID:
            return _uuid.UUID(text)
        if decoder_id == _DECODER_DECIMAL:
            return _dc.Decimal(text)
        if decoder_id == _DECODER_DATETIME:
            return _dt.datetime.fromisoformat(text)
        if decoder_id == _DECODER_DATE:
            return _dt.date.fromisoformat(text)
        if decoder_id == _DECODER_TIME:
            return _dt.time.fromisoformat(text)
        return value

    @staticmethod
    def _parse_query_pairs(raw_query: bytes) -> tuple[tuple[int, str], ...]:
        if not raw_query:
            return ()
        out: list[tuple[int, str]] = []
        for chunk in raw_query.split(b"&"):
            if not chunk:
                continue
            raw_key, _, raw_value = chunk.partition(b"=")
            try:
                key = unquote_plus(raw_key.decode("latin-1"))
                value = unquote_plus(raw_value.decode("latin-1"))
            except Exception:
                continue
            out.append((PackedPlanExecutor._stable_name_hash64(key), value))
        return tuple(out)

    @classmethod
    def _ensure_hot_request(cls, ctx: _Ctx, hot: HotCtx) -> Request | Any | None:
        request = getattr(ctx, "request", None)
        if request is not None:
            return request
        raw_scope = hot.raw_scope
        if not isinstance(raw_scope, Mapping):
            return None
        request = Request(dict(raw_scope), app=getattr(ctx, "app", None))
        if hot.body_bytes is not None:
            request.body = hot.body_bytes
        ctx.request = request
        return request

    @staticmethod
    async def _ensure_body_bytes(ctx: _Ctx, hot: HotCtx) -> bytes:
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

    @classmethod
    def _body_hash_items(cls, body: Any) -> tuple[tuple[int, Any], ...]:
        if not isinstance(body, Mapping):
            return ()
        out: list[tuple[int, Any]] = []
        for key, value in body.items():
            if not isinstance(key, str):
                continue
            out.append((cls._stable_name_hash64(key), value))
        return tuple(out)

    @classmethod
    def _param_shape_descriptor_slice(
        cls,
        packed: PackedKernel,
        param_shape_id: int,
    ) -> tuple[int, int]:
        offsets = cls._hot_array(
            packed,
            "param_shape_offsets",
            tuple(getattr(packed, "param_shape_offsets", ()) or ()),
        )
        lengths = cls._hot_array(
            packed,
            "param_shape_lengths",
            tuple(getattr(packed, "param_shape_lengths", ()) or ()),
        )
        if not (0 <= param_shape_id < len(offsets)):
            return (0, 0)
        return int(offsets[param_shape_id]), int(lengths[param_shape_id])

    @classmethod
    def _segment_phase_names(cls, packed: PackedKernel) -> tuple[str, ...]:
        phase_names = tuple(getattr(packed, "phase_names", ()) or ())
        phase_ids = cls._hot_array(
            packed,
            "segment_phase_ids",
            tuple(getattr(packed, "segment_catalog_phase_ids", ()) or ()),
        )
        if phase_names and phase_ids:
            return tuple(
                str(phase_names[int(phase_id)]) if 0 <= int(phase_id) < len(phase_names) else str(phase_id)
                for phase_id in phase_ids
        )
        return tuple(getattr(packed, "segment_phases", ()) or ())

    @classmethod
    def _resolve_program_param_shape_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(getattr(hot_op_plan, "param_shape_id", None))
            if plan_value is not None:
                return plan_value
        values = cls._hot_array(
            packed,
            "program_param_shape_ids",
            tuple(getattr(packed, "program_param_shape_ids", ()) or ()),
        )
        if 0 <= program_id < len(values):
            return int(values[program_id])
        return -1

    @classmethod
    def _resolve_program_transport_kind_id(
        cls, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> int:
        if hot_op_plan is not None:
            plan_value = cls._coerce_int(
                getattr(hot_op_plan, "transport_kind_id", None)
            )
            if plan_value is not None:
                return plan_value
        values = cls._hot_array(
            packed,
            "program_transport_kind_ids",
            tuple(getattr(packed, "program_transport_kind_ids", ()) or ()),
        )
        if 0 <= program_id < len(values):
            return int(values[program_id])
        return _TRANSPORT_KIND_GENERIC

    @staticmethod
    def _active_transport_kind(
        hot: HotCtx,
        dispatch: Mapping[str, Any] | None,
        fallback: int,
    ) -> int:
        protocol = ""
        if isinstance(dispatch, Mapping):
            protocol = str(dispatch.get("binding_protocol") or "")
        if not protocol:
            protocol = str(hot.protocol or "")
        if protocol.endswith(".jsonrpc"):
            return _TRANSPORT_KIND_JSONRPC
        if protocol.endswith(".rest"):
            return _TRANSPORT_KIND_REST
        if protocol in {"ws", "wss", "webtransport"}:
            return _TRANSPORT_KIND_CHANNEL
        return fallback

    @classmethod
    async def _prepare_compiled_input(
        cls,
        ctx: _Ctx,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> None:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp
        hot = temp.get("hot_ctx")
        if not isinstance(hot, HotCtx):
            return
        param_shape_id = cls._resolve_program_param_shape_id(packed, program_id, hot_op_plan)
        if param_shape_id < 0:
            return
        if hot.slot_values is not None and hot.param_shape_id == param_shape_id:
            return

        hot.param_shape_id = param_shape_id
        hot.transport_kind_id = cls._resolve_program_transport_kind_id(
            packed, program_id, hot_op_plan
        )
        raw_scope = hot.raw_scope if isinstance(hot.raw_scope, Mapping) else {}
        if hot.raw_headers is None:
            hot.raw_headers = cls._coerce_header_pairs(raw_scope)
        if not hot.content_type:
            hot.content_type = cls._content_type_from_raw_headers(hot.raw_headers or ())
        if not hot.raw_query_string and isinstance(raw_scope, Mapping):
            query_string = raw_scope.get("query_string", b"")
            if isinstance(query_string, (bytes, bytearray)):
                hot.raw_query_string = bytes(query_string)
        if hot.path_params is None:
            route = temp.get("route")
            if isinstance(route, Mapping) and isinstance(route.get("path_params"), Mapping):
                hot.path_params = route.get("path_params")
            elif isinstance(raw_scope, Mapping) and isinstance(raw_scope.get("path_params"), Mapping):
                hot.path_params = raw_scope.get("path_params")
        request = cls._ensure_hot_request(ctx, hot)
        body_bytes = await cls._ensure_body_bytes(ctx, hot)
        if request is not None and body_bytes is not None and hasattr(request, "body"):
            request.body = body_bytes
        if hot.transport_kind_id in {_TRANSPORT_KIND_REST, _TRANSPORT_KIND_JSONRPC}:
            if not hot.parsed_json_loaded:
                parsed = None
                if body_bytes and "json" in hot.content_type:
                    try:
                        parsed = json.loads(body_bytes)
                    except Exception:
                        parsed = None
                hot.parsed_json = parsed
                hot.parsed_json_loaded = True

        dispatch = temp.setdefault("dispatch", {})
        route = temp.setdefault("route", {})
        hot.transport_kind_id = cls._active_transport_kind(
            hot,
            dispatch if isinstance(dispatch, Mapping) else None,
            hot.transport_kind_id,
        )
        if isinstance(dispatch, dict):
            dispatch.setdefault("binding_protocol", hot.protocol)
            dispatch.setdefault("binding_selector", hot.selector)
        if isinstance(route, dict):
            route.setdefault("protocol", hot.protocol)
            route.setdefault("selector", hot.selector)
            route.setdefault("program_id", program_id)
            route.setdefault("opmeta_index", program_id)
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(hot.parsed_json, Mapping):
            rpc_envelope = hot.parsed_json if isinstance(hot.parsed_json, dict) else dict(hot.parsed_json)
            if isinstance(dispatch, dict):
                dispatch["rpc"] = rpc_envelope
                dispatch["rpc_method"] = rpc_envelope.get("method")
                dispatch["parsed_payload"] = rpc_envelope.get("params", {})
            if isinstance(route, dict):
                route["rpc_envelope"] = rpc_envelope
            temp["jsonrpc_request_id"] = rpc_envelope.get("id")

        start, length = cls._param_shape_descriptor_slice(packed, param_shape_id)
        if length <= 0:
            return
        lookup_hashes = cls._hot_array(
            packed,
            "param_shape_lookup_hashes",
            tuple(getattr(packed, "param_shape_lookup_hashes", ()) or ()),
        )
        header_hashes = cls._hot_array(
            packed,
            "param_shape_header_hashes",
            tuple(getattr(packed, "param_shape_header_hashes", ()) or ()),
        )
        source_masks = cls._hot_array(
            packed,
            "param_shape_source_masks",
            tuple(getattr(packed, "param_shape_source_masks", ()) or ()),
        )
        slot_ids = cls._hot_array(
            packed,
            "param_shape_slot_ids",
            tuple(getattr(packed, "param_shape_slot_ids", ()) or ()),
        )
        decoder_ids = cls._hot_array(
            packed,
            "param_shape_decoder_ids",
            tuple(getattr(packed, "param_shape_decoder_ids", ()) or ()),
        )
        max_lengths = cls._hot_array(
            packed,
            "param_shape_max_lengths",
            tuple(getattr(packed, "param_shape_max_lengths", ()) or ()),
        )

        body_payload = hot.parsed_json
        if hot.transport_kind_id == _TRANSPORT_KIND_JSONRPC and isinstance(body_payload, Mapping):
            body_payload = body_payload.get("params", {})
        body_items = cls._body_hash_items(body_payload)
        query_pairs = cls._parse_query_pairs(hot.raw_query_string)
        raw_headers = hot.raw_headers or ()
        path_pairs = tuple(
            (
                cls._stable_name_hash64(str(key)),
                value,
            )
            for key, value in ((hot.path_params or {}) if isinstance(hot.path_params, Mapping) else {}).items()
        )
        opview = getattr(ctx, "opview", None)
        schema_in = getattr(opview, "schema_in", None) if opview is not None else None
        field_names = tuple(getattr(schema_in, "fields", ()) or ())
        slot_values: list[Any] = [None] * len(field_names)
        slot_present = bytearray(len(field_names))

        def _lookup(items: tuple[tuple[int, Any], ...], target_hash: int) -> tuple[bool, Any]:
            for item_hash, item_value in items:
                if int(item_hash) == int(target_hash):
                    return True, item_value
            return False, None

        for idx in range(start, start + length):
            slot_id = int(slot_ids[idx])
            if not (0 <= slot_id < len(slot_values)):
                continue
            lookup_hash = int(lookup_hashes[idx])
            header_hash = int(header_hashes[idx]) if idx < len(header_hashes) else 0
            source_mask = int(source_masks[idx]) if idx < len(source_masks) else 0
            decoder_id = int(decoder_ids[idx]) if idx < len(decoder_ids) else _DECODER_NONE
            value = None
            found = False
            if source_mask & _PARAM_SOURCE_BODY:
                found, value = _lookup(body_items, lookup_hash)
            if not found and source_mask & _PARAM_SOURCE_PATH:
                found, value = _lookup(path_pairs, lookup_hash)
            if not found and source_mask & _PARAM_SOURCE_QUERY:
                found, value = _lookup(query_pairs, lookup_hash)
            if not found and source_mask & _PARAM_SOURCE_HEADER and header_hash:
                for key_bytes, raw_value in raw_headers:
                    if cls._stable_name_hash64(
                        key_bytes.decode("latin-1"), lowercase=True
                    ) == header_hash:
                        found = True
                        value = raw_value.decode("latin-1")
                        break
            if not found:
                continue
            try:
                coerced = cls._decode_scalar(value, decoder_id)
            except Exception:
                coerced = value
            max_length = int(max_lengths[idx]) if idx < len(max_lengths) else 0
            if max_length > 0 and isinstance(coerced, str) and len(coerced) > max_length:
                coerced = coerced[:max_length]
            slot_values[slot_id] = coerced
            slot_present[slot_id] = 1

        hot.slot_values = slot_values
        hot.slot_present = slot_present
        in_values = {
            field_names[idx]: slot_values[idx]
            for idx in range(len(field_names))
            if slot_present[idx]
        }
        temp["compiled_in_values_ready"] = True
        temp["in_values"] = in_values
        temp["in_present"] = tuple(
            field_names[idx] for idx in range(len(field_names)) if slot_present[idx]
        )
        if in_values:
            ctx.payload = in_values
            if isinstance(route, dict):
                route["payload"] = in_values
            if isinstance(dispatch, dict):
                dispatch["normalized_input"] = in_values
                if "parsed_payload" not in dispatch:
                    dispatch["parsed_payload"] = in_values
        if hot.path_params:
            ctx.path_params = dict(hot.path_params)
            if isinstance(route, dict):
                route["path_params"] = dict(hot.path_params)
        hot.lazy_published = True

    def _resolve_segments_for_program(
        self, packed: PackedKernel, program_id: int
    ) -> tuple[tuple[int, ...], tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_segments_cache.get(cache_key)
        if cached is not None:
            return cached

        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[program_id]
        seg_length = segment_lengths[program_id]
        ordered_segments: list[int] = []
        by_phase: dict[str, list[int]] = {}
        remaining: list[int] = []
        seen_segment_ids: set[int] = set()
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase = str(normalize_phase(segment_phases[seg_id]))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            by_phase.setdefault(phase, []).append(seg_id)

        for phase in self._PHASE_EXECUTION_ORDER:
            for seg_id in by_phase.pop(phase, ()):  # pragma: no branch
                if seg_id in seen_segment_ids:
                    continue
                seen_segment_ids.add(seg_id)
                ordered_segments.append(seg_id)

        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            if seg_id in seen_segment_ids:
                continue
            phase = str(segment_phases[seg_id])
            phase = str(normalize_phase(phase))
            if phase.startswith("ON_") or phase == "TX_ROLLBACK":
                continue
            seen_segment_ids.add(seg_id)
            remaining.append(seg_id)

        resolved = (tuple(ordered_segments), tuple(remaining))
        self._program_segments_cache[cache_key] = resolved
        return resolved

    @staticmethod
    def _coerce_int(value: Any) -> int | None:
        return value if isinstance(value, int) else None

    @staticmethod
    def _ensure_hot_ctx(ctx: _Ctx, env: Any) -> HotCtx:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp
        hot = temp.get("hot_ctx")
        if isinstance(hot, HotCtx):
            return hot

        scope = getattr(env, "scope", {}) or {}
        method = str(scope.get("method") or "").upper()
        path = str(scope.get("path") or "")
        scheme = str(scope.get("scheme") or "").lower()
        scope_type = str(scope.get("type") or "")
        protocol = ""
        selector = ""
        if scope_type == "http" and method and path:
            protocol = "https.rest" if scheme == "https" else "http.rest"
            selector = f"{method} {path}"
        elif scope_type in {"websocket", "webtransport"} and path:
            protocol = scheme or scope_type
            selector = path

        hot = HotCtx(
            scope_type=scope_type,
            method=method,
            path=path,
            protocol=protocol,
            selector=selector,
            content_type="",
            raw_scope=scope if isinstance(scope, Mapping) else None,
            raw_receive=getattr(env, "receive", None),
            raw_headers=PackedPlanExecutor._coerce_header_pairs(scope if isinstance(scope, Mapping) else None),
            raw_query_string=bytes(scope.get("query_string", b""))
            if isinstance(scope, Mapping)
            and isinstance(scope.get("query_string", b""), (bytes, bytearray))
            else b"",
            path_params=scope.get("path_params")
            if isinstance(scope, Mapping) and isinstance(scope.get("path_params"), Mapping)
            else None,
        )
        temp["hot_ctx"] = hot
        return hot

    @staticmethod
    def _coerce_model_column_keys(obj: Any) -> tuple[str, ...] | None:
        table = getattr(obj, "__table__", None)
        columns = getattr(table, "columns", None)
        if columns is None:
            return None
        out: list[str] = []
        for col in columns:
            key = getattr(col, "key", None)
            if isinstance(key, str) and key:
                out.append(key)
        return tuple(out)

    def _serialize_model_row(self, obj: Any) -> Any:
        if obj is None or isinstance(obj, Mapping):
            return obj
        model_type = type(obj)
        serializer = self._model_row_serializer_cache.get(model_type)
        if serializer is None:
            keys = self._coerce_model_column_keys(obj)
            if keys is None:
                return obj
            getter = attrgetter(*keys)
            serializer = (keys, getter)
            self._model_row_serializer_cache[model_type] = serializer
        keys, getter = serializer
        if not keys:
            return obj
        values = getter(obj)
        if len(keys) == 1:
            values = (values,)
        return dict(zip(keys, values))

    def _require_program_id_from_ctx(self, ctx: _Ctx) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        route = temp.get("route") if isinstance(temp, dict) else None
        if isinstance(route, dict):
            for key in ("program_id", "opmeta_index"):
                value = self._coerce_int(route.get(key))
                if value is not None:
                    temp["program_id"] = value
                    return value

        value = self._coerce_int(temp.get("program_id"))
        if value is not None:
            return value

        return -1

    def _resolve_program_id_from_dispatch(self, ctx: _Ctx, packed: PackedKernel) -> int:
        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        hot = temp.get("hot_ctx")
        if isinstance(hot, HotCtx) and hot.program_id >= 0:
            route = temp.setdefault("route", {})
            if isinstance(route, dict):
                route.setdefault("program_id", hot.program_id)
                route.setdefault("opmeta_index", hot.program_id)
            temp["program_id"] = hot.program_id
            return hot.program_id

        dispatch = temp.get("dispatch")
        if not isinstance(dispatch, dict):
            return -1

        selector = dispatch.get("binding_selector")
        protocol = dispatch.get("binding_protocol")
        if not (isinstance(selector, str) and isinstance(protocol, str)):
            return -1

        selector_to_id = getattr(packed, "selector_to_id", None)
        proto_to_id = getattr(packed, "proto_to_id", None)
        route_to_program = getattr(packed, "route_to_program", None)
        if not (
            isinstance(selector_to_id, Mapping)
            and isinstance(proto_to_id, Mapping)
            and route_to_program is not None
        ):
            return -1

        if isinstance(hot, HotCtx) and hot.selector == selector and hot.protocol == protocol:
            selector_id = hot.selector_id if hot.selector_id >= 0 else None
            proto_id = hot.proto_id if hot.proto_id >= 0 else None
        else:
            selector_id = self._coerce_int(selector_to_id.get(selector))
            proto_id = self._coerce_int(proto_to_id.get(protocol))
        if selector_id is None or proto_id is None:
            return -1
        if not (0 <= proto_id < len(route_to_program)):
            return -1

        row = route_to_program[proto_id]
        if not (0 <= selector_id < len(row)):
            return -1

        program_id = self._coerce_int(row[selector_id])
        if program_id is None or program_id < 0:
            return -1

        route = temp.setdefault("route", {})
        if isinstance(route, dict):
            route.setdefault("program_id", program_id)
            route.setdefault("opmeta_index", program_id)
        temp["program_id"] = program_id
        if isinstance(hot, HotCtx):
            hot.program_id = program_id
        return program_id

    def _resolve_request_caches(
        self, plan: KernelPlan
    ) -> tuple[dict[tuple[int, str, str], int], tuple[tuple[str, Any, int], ...]]:
        plan_id = id(plan)
        templated = self._templated_route_cache.get(plan_id)
        if templated is None:
            exact: dict[tuple[int, str, str], int] = {}
            templated_routes: list[tuple[str, Any, int]] = []
            for proto in ("http.rest", "https.rest"):
                bucket = plan.proto_indices.get(proto)
                if not isinstance(bucket, Mapping):
                    continue
                exact_bucket = bucket.get("exact")
                if isinstance(exact_bucket, Mapping):
                    for selector, meta_index in exact_bucket.items():
                        if not (
                            isinstance(selector, str) and isinstance(meta_index, int)
                        ):
                            continue
                        method, _, path = selector.partition(" ")
                        if not path:
                            continue
                        exact[(plan_id, method.upper(), path)] = meta_index
                templated_bucket = bucket.get("templated")
                if isinstance(templated_bucket, list):
                    for entry in templated_bucket:
                        if not isinstance(entry, Mapping):
                            continue
                        meta_index = entry.get("meta_index")
                        pattern = entry.get("pattern")
                        if (
                            not isinstance(meta_index, int)
                            or pattern is None
                            or not hasattr(pattern, "match")
                        ):
                            continue
                        method = str(entry.get("method", "") or "").upper()
                        templated_routes.append((method, pattern, meta_index))
            self._request_program_cache.update(exact)
            templated = tuple(templated_routes)
            self._templated_route_cache[plan_id] = templated
        return self._request_program_cache, templated

    def _resolve_program_id_from_request(self, ctx: _Ctx, plan: KernelPlan) -> int:
        method = getattr(ctx, "method", None)
        path = getattr(ctx, "path", None)

        if not (isinstance(method, str) and isinstance(path, str) and path):
            raw = getattr(ctx, "raw", None)
            scope = getattr(raw, "scope", None) if raw is not None else None
            if isinstance(scope, Mapping):
                method = method or scope.get("method")
                path = path or scope.get("path")

        if not (isinstance(method, str) and isinstance(path, str) and path):
            return -1

        method = method.upper()
        exact_cache, templated_routes = self._resolve_request_caches(plan)
        maybe = exact_cache.get((id(plan), method, path))
        if isinstance(maybe, int):
            return maybe

        selector = f"{method} {path}"
        for proto in ("http.rest", "https.rest"):
            maybe = plan.opkey_to_meta.get(OpKey(proto=proto, selector=selector))
            if isinstance(maybe, int):
                exact_cache[(id(plan), method, path)] = maybe
                return maybe

        for entry_method, pattern, meta_index in templated_routes:
            if entry_method and entry_method != method:
                continue
            if pattern.match(path) is None:
                continue
            exact_cache[(id(plan), method, path)] = meta_index
            return meta_index

        return -1

    def _resolve_program_id_from_channel(
        self,
        ctx: _Ctx,
        plan: KernelPlan,
    ) -> int:
        channel = ctx.get("channel")
        protocol = getattr(channel, "protocol", None)
        path = getattr(channel, "path", None)
        if not (isinstance(protocol, str) and isinstance(path, str) and path):
            return -1

        for proto in (protocol, "ws", "wss", "webtransport"):
            bucket = plan.proto_indices.get(proto)
            if not isinstance(bucket, Mapping):
                continue
            exact_bucket = bucket.get("exact")
            if isinstance(exact_bucket, Mapping):
                maybe = exact_bucket.get(path)
                if isinstance(maybe, int):
                    return maybe
            templated_bucket = bucket.get("templated")
            if isinstance(templated_bucket, list):
                for entry in templated_bucket:
                    if not isinstance(entry, Mapping):
                        continue
                    pattern = entry.get("pattern")
                    meta_index = entry.get("meta_index")
                    if hasattr(pattern, "match") and isinstance(meta_index, int):
                        matched = pattern.match(path)
                        if matched is not None:
                            channel = ctx.get("channel")
                            if channel is not None:
                                channel.path_params = matched.groupdict()
                            temp = getattr(ctx, "temp", None)
                            if isinstance(temp, dict):
                                temp.setdefault("dispatch", {})["path_params"] = matched.groupdict()
                                temp.setdefault("route", {})["path_params"] = matched.groupdict()
                            return meta_index
        return -1

    @staticmethod
    def _resolve_program_id_from_exact_route(
        packed: PackedKernel, method: str, path: str
    ) -> int:
        route = getattr(packed, "rest_exact_route_to_program", None)
        if not isinstance(route, Mapping):
            return -1
        maybe = route.get((method.upper(), path))
        return maybe if isinstance(maybe, int) else -1

    def _prime_exact_route_program(
        self, ctx: _Ctx, env: Any, packed: PackedKernel
    ) -> int:
        hot = self._ensure_hot_ctx(ctx, env)
        if hot.scope_type != "http" or not hot.method or not hot.path:
            return -1
        program_id = self._resolve_program_id_from_exact_route(
            packed, hot.method, hot.path
        )
        if program_id < 0:
            return -1

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            return -1

        proto_to_id = getattr(packed, "proto_to_id", None)
        selector_to_id = getattr(packed, "selector_to_id", None)
        if isinstance(proto_to_id, Mapping):
            proto_id = self._coerce_int(proto_to_id.get(hot.protocol))
            if proto_id is not None:
                hot.proto_id = proto_id
        if isinstance(selector_to_id, Mapping):
            selector_id = self._coerce_int(selector_to_id.get(hot.selector))
            if selector_id is not None:
                hot.selector_id = selector_id
        hot.program_id = program_id

        ctx.method = hot.method
        ctx.path = hot.path
        dispatch = temp.setdefault("dispatch", {})
        if isinstance(dispatch, dict):
            dispatch.setdefault("binding_protocol", hot.protocol)
            dispatch.setdefault("binding_selector", hot.selector)
            dispatch.setdefault("channel_protocol", hot.protocol)
            dispatch.setdefault("channel_selector", hot.selector)
        route = temp.setdefault("route", {})
        if isinstance(route, dict):
            route.setdefault("selector", hot.selector)
            route.setdefault("protocol", hot.protocol)
            route.setdefault("program_id", program_id)
            route.setdefault("opmeta_index", program_id)
        temp["program_id"] = program_id
        return program_id

    async def _probe_ingress_for_program(
        self, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> int:
        if not getattr(plan, "opmeta", None):
            return -1

        seed_program_id = 0
        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[seed_program_id]
        seg_length = segment_lengths[seed_program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase = str(segment_phases[seg_id])
            if not phase.startswith("INGRESS_"):
                break
            await self._run_segment(ctx, packed, seg_id)

        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp["ingress_probed"] = True

        return self._require_program_id_from_ctx(ctx)

    def _resolve_segment_step_ids(
        self, packed: PackedKernel
    ) -> tuple[tuple[int, ...], ...]:
        packed_id = id(packed)
        cached = self._segment_steps_cache.get(packed_id)
        if cached is not None:
            return cached
        segment_offsets = self._hot_array(
            packed,
            "segment_step_offsets",
            tuple(getattr(packed, "segment_catalog_offsets", ()) or getattr(packed, "segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "segment_step_lengths",
            tuple(getattr(packed, "segment_catalog_lengths", ()) or getattr(packed, "segment_lengths", ()) or ()),
        )
        segment_atom_ids = self._hot_array(
            packed,
            "segment_step_atom_refs",
            tuple(getattr(packed, "segment_catalog_atom_ids", ()) or getattr(packed, "segment_step_ids", ()) or ()),
        )
        compiled = []
        for segment_index in range(len(segment_offsets)):
            start = segment_offsets[segment_index]
            end = start + segment_lengths[segment_index]
            compiled.append(
                tuple(segment_atom_ids[idx] for idx in range(start, end))
            )
        frozen = tuple(compiled)
        self._segment_steps_cache[packed_id] = frozen
        return frozen

    def _resolve_segment_runners(self, packed: PackedKernel) -> tuple[Any, ...]:
        packed_id = id(packed)
        cached = self._segment_runners_cache.get(packed_id)
        if cached is not None:
            return cached

        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        executor_kinds = tuple(
            self._hot_array(
                packed,
                "segment_executor_kind_ids",
                tuple(getattr(packed, "segment_catalog_executor_kinds", ()) or getattr(packed, "segment_executor_kinds", ()) or ()),
            )
        )

        step_table = packed.step_table

        def _make_fused_sync_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    step(ctx)

            return _runner

        def _make_async_direct_runner(step_ids: tuple[int, ...]):
            steps = tuple(step_table[step_id] for step_id in step_ids)

            async def _runner(ctx: _Ctx) -> None:
                for step in steps:
                    await step(ctx)

            return _runner

        def _make_mixed_runner(step_ids: tuple[int, ...]):
            steps = tuple(
                (
                    step_table[step_id],
                    async_flags[step_id] if step_id < len(async_flags) else False,
                )
                for step_id in step_ids
            )

            async def _runner(ctx: _Ctx) -> None:
                for step, is_async in steps:
                    if is_async:
                        await step(ctx)
                        continue
                    rv = step(ctx)
                    if inspect.isawaitable(rv):
                        await rv

            return _runner

        runners: list[Any] = []
        for seg_id, step_ids in enumerate(step_ids_by_segment):
            executor_kind = executor_kinds[seg_id] if seg_id < len(executor_kinds) else ""
            if executor_kind in {"sync.extractable", 1}:
                runners.append(_make_fused_sync_runner(step_ids))
            elif executor_kind in {"async.direct", 3}:
                runners.append(_make_async_direct_runner(step_ids))
            else:
                runners.append(_make_mixed_runner(step_ids))

        frozen = tuple(runners)
        self._segment_runners_cache[packed_id] = frozen
        return frozen

    @classmethod
    def _resolve_program_hot_runner_id(
        cls,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> int:
        if hot_op_plan is not None:
            program_hot_runner_id = cls._coerce_int(
                getattr(hot_op_plan, "program_hot_runner_id", None)
            )
            if program_hot_runner_id is not None:
                return program_hot_runner_id
        hot_runner_ids = cls._hot_array(
            packed,
            "program_hot_runner_ids",
            tuple(getattr(packed, "program_hot_runner_ids", ()) or ()),
        )
        if 0 <= program_id < len(hot_runner_ids):
            return int(hot_runner_ids[program_id])
        return _HOT_RUNNER_GENERIC

    def _resolve_program_linear_direct_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_LINEAR_DIRECT)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)

        phase_names = self._segment_phase_names(packed)
        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        step_table = packed.step_table
        for seg_id in (*ordered, *remaining):
            phase_name = str(normalize_phase(phase_names[seg_id]))
            for step_id in step_ids_by_segment[seg_id]:
                step = step_table[step_id]
                direct_run = getattr(step, "__tigrbl_direct_run", None)
                if callable(direct_run):
                    direct_dep = getattr(step, "__tigrbl_direct_dep", None)
                    has_direct_dep = bool(
                        getattr(step, "__tigrbl_has_direct_dep", False)
                    )
                    direct_is_async = bool(
                        getattr(step, "__tigrbl_direct_is_async", False)
                    )
                    use_two_args = bool(getattr(step, "__tigrbl_use_two_args", False))
                    invoke_kind = (
                        _DIRECT_INVOKE_RUN_WITH_DEP
                        if has_direct_dep
                        else (
                            _DIRECT_INVOKE_RUN_WITH_NONE
                            if use_two_args
                            else _DIRECT_INVOKE_RUN
                        )
                    )
                    compiled_steps.append(
                        (
                            phase_name,
                            invoke_kind,
                            direct_run,
                            direct_dep,
                            direct_is_async,
                        )
                    )
                    continue
                compiled_steps.append(
                    (
                        phase_name,
                        _DIRECT_INVOKE_STEP,
                        step,
                        None,
                        bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )
                )

        async def _runner(ctx: _Ctx) -> None:
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
                if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                    rv = call(dep, ctx)
                elif invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                    rv = call(None, ctx)
                else:
                    rv = call(ctx)
                if is_async:
                    await rv
                elif inspect.isawaitable(rv):
                    await rv

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_compiled_param_runner(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(packed), program_id, _HOT_RUNNER_COMPILED_PARAM)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached

        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)

        phase_names = self._segment_phase_names(packed)
        step_ids_by_segment = self._resolve_segment_step_ids(packed)
        async_flags = tuple(
            1 if bool(flag) else 0
            for flag in self._hot_array(
                packed,
                "atom_flags",
                tuple(
                    getattr(packed, "atom_catalog_async_flags", ())
                    or getattr(packed, "step_async_flags", ())
                    or ()
                ),
            )
        )
        opcode_ids = tuple(
            int(value)
            for value in self._hot_array(
                packed,
                "atom_opcode_ids",
                tuple(getattr(packed, "atom_catalog_opcode_ids", ()) or ()),
            )
        )
        opcode_keys = tuple(getattr(packed, "atom_opcode_keys", ()) or ())
        skip_step_ids: set[int] = set()
        skip_names = {
            "ingress.transport_extract",
            "ingress.input_prepare",
            "dispatch.binding_match",
            "dispatch.binding_parse",
            "dispatch.input_normalize",
            "wire.build_in",
        }
        for step_id, opcode_id in enumerate(opcode_ids):
            if 0 <= opcode_id < len(opcode_keys):
                if str(opcode_keys[opcode_id]) in skip_names:
                    skip_step_ids.add(step_id)

        compiled_steps: list[tuple[str, int, Any, Any, bool]] = []
        step_table = packed.step_table
        for seg_id in (*ordered, *remaining):
            phase_name = str(normalize_phase(phase_names[seg_id]))
            for step_id in step_ids_by_segment[seg_id]:
                if step_id in skip_step_ids:
                    continue
                step = step_table[step_id]
                direct_run = getattr(step, "__tigrbl_direct_run", None)
                if callable(direct_run):
                    direct_dep = getattr(step, "__tigrbl_direct_dep", None)
                    has_direct_dep = bool(
                        getattr(step, "__tigrbl_has_direct_dep", False)
                    )
                    direct_is_async = bool(
                        getattr(step, "__tigrbl_direct_is_async", False)
                    )
                    use_two_args = bool(getattr(step, "__tigrbl_use_two_args", False))
                    invoke_kind = (
                        _DIRECT_INVOKE_RUN_WITH_DEP
                        if has_direct_dep
                        else (
                            _DIRECT_INVOKE_RUN_WITH_NONE
                            if use_two_args
                            else _DIRECT_INVOKE_RUN
                        )
                    )
                    compiled_steps.append(
                        (
                            phase_name,
                            invoke_kind,
                            direct_run,
                            direct_dep,
                            direct_is_async,
                        )
                    )
                    continue
                compiled_steps.append(
                    (
                        phase_name,
                        _DIRECT_INVOKE_STEP,
                        step,
                        None,
                        bool(async_flags[step_id]) if step_id < len(async_flags) else False,
                    )
                )

        async def _runner(ctx: _Ctx) -> None:
            await self._prepare_compiled_input(ctx, packed, program_id, hot_op_plan)
            current_phase = ""
            for phase_name, invoke_kind, call, dep, is_async in compiled_steps:
                if phase_name != current_phase:
                    ctx.phase = phase_name
                    current_phase = phase_name
                if invoke_kind == _DIRECT_INVOKE_RUN_WITH_DEP:
                    rv = call(dep, ctx)
                elif invoke_kind == _DIRECT_INVOKE_RUN_WITH_NONE:
                    rv = call(None, ctx)
                else:
                    rv = call(ctx)
                if is_async:
                    await rv
                elif inspect.isawaitable(rv):
                    await rv

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner(
        self, packed: PackedKernel, program_id: int, hot_op_plan: Any | None
    ) -> Any:
        cache_key = (id(packed), program_id)
        cached = self._program_runner_cache.get(cache_key)
        if cached is not None:
            return cached
        program_hot_runner_id = self._resolve_program_hot_runner_id(
            packed, program_id, hot_op_plan
        )
        if program_hot_runner_id == _HOT_RUNNER_COMPILED_PARAM:
            runner = self._resolve_program_compiled_param_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        if program_hot_runner_id == _HOT_RUNNER_LINEAR_DIRECT:
            runner = self._resolve_program_linear_direct_runner(
                packed, program_id, hot_op_plan
            )
            self._program_runner_cache[cache_key] = runner
            return runner
        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        async def _runner(ctx: _Ctx) -> None:
            temp = getattr(ctx, "temp", None)
            skip_dispatch = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_exact_route")
            )
            fast_direct_create = bool(
                isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create")
            )
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if skip_dispatch and phase_name in {
                    "INGRESS_BEGIN",
                    "INGRESS_DISPATCH",
                }:
                    continue
                if fast_direct_create and phase_name in {
                    "POST_COMMIT",
                    "EGRESS_SHAPE",
                    "EGRESS_FINALIZE",
                    "POST_RESPONSE",
                }:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_cache[cache_key] = _runner
        return _runner

    def _resolve_program_runner_for_mode(
        self,
        packed: PackedKernel,
        program_id: int,
        hot_op_plan: Any | None,
        *,
        skip_dispatch: bool = False,
        fast_direct_create: bool = False,
    ) -> Any:
        mode = (1 if skip_dispatch else 0) | (2 if fast_direct_create else 0)
        cache_key = (id(packed), program_id, mode)
        cached = self._program_runner_mode_cache.get(cache_key)
        if cached is not None:
            return cached

        base_runner = self._resolve_program_runner(packed, program_id, hot_op_plan)
        if not skip_dispatch and not fast_direct_create:
            self._program_runner_mode_cache[cache_key] = base_runner
            return base_runner

        runners = self._resolve_segment_runners(packed)
        if hot_op_plan is not None:
            ordered = tuple(getattr(hot_op_plan, "ordered_segment_ids", ()) or ())
            remaining = tuple(getattr(hot_op_plan, "remaining_segment_ids", ()) or ())
        else:
            ordered, remaining = self._resolve_segments_for_program(packed, program_id)
        phase_names = self._segment_phase_names(packed)
        all_segment_ids = (*ordered, *remaining)

        skip_phases = set()
        if skip_dispatch:
            skip_phases.update({"INGRESS_BEGIN", "INGRESS_DISPATCH"})
        if fast_direct_create:
            skip_phases.update(
                {"POST_COMMIT", "EGRESS_SHAPE", "EGRESS_FINALIZE", "POST_RESPONSE"}
            )

        async def _runner(ctx: _Ctx) -> None:
            for seg_id in all_segment_ids:
                phase_name = str(normalize_phase(phase_names[seg_id]))
                if phase_name in skip_phases:
                    continue
                ctx.phase = phase_name
                await runners[seg_id](ctx)

        self._program_runner_mode_cache[cache_key] = _runner
        return _runner

    def _resolve_db_acquire(
        self,
        plan: KernelPlan,
        program_id: int,
        hot_op_plan: Any | None,
    ) -> Any:
        cache_key = (id(plan), program_id)
        cached = self._db_acquire_cache.get(cache_key)
        if cached is not None:
            return cached
        model = getattr(hot_op_plan, "model", None)
        alias = getattr(hot_op_plan, "alias", None)
        hint = str(getattr(hot_op_plan, "db_acquire_hint", "resolver") or "resolver")

        if hint == "model_get_db" and callable(
            getattr(model, "__tigrbl_get_db__", None)
        ):
            _resolver = import_module("tigrbl_concrete._concrete").engine_resolver

            def _acquire(_ctx: _Ctx) -> tuple[Any, Any]:
                return _resolver.acquire(model=model)

            self._db_acquire_cache[cache_key] = _acquire
            return _acquire

        provider_cache: dict[str, Any] = {}
        app_resolver_cache: dict[str, Any] = {}

        def _runtime_owner(ctx: _Ctx) -> Any:
            return getattr(ctx, "router", None) or getattr(ctx, "app", None)

        def _resolve_from_owner(ctx: _Ctx) -> Any:
            owner = _runtime_owner(ctx)
            if owner is None:
                return None
            if "resolver" in app_resolver_cache:
                return app_resolver_cache["resolver"]
            resolver = getattr(owner, "_tigrbl_runtime_resolve_provider", None)
            if callable(resolver):
                app_resolver_cache["resolver"] = resolver
                return resolver
            return None

        def _acquire_via_owner(ctx: _Ctx) -> tuple[Any, Any] | None:
            owner = _runtime_owner(ctx)
            acquire = getattr(owner, "_tigrbl_runtime_acquire_db", None)
            if callable(acquire):
                return acquire(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            return None

        def _release(db: Any) -> None:
            close = getattr(db, "close", None)
            if not callable(close):
                return
            try:
                rv = close()
                if inspect.isawaitable(rv):
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        asyncio.run(rv)
                    else:
                        loop.create_task(rv)
            except Exception:
                return

        def _acquire_from_provider(provider: Any) -> tuple[Any, Any]:
            db = provider.session()
            return db, lambda: _release(db)

        def _acquire(ctx: _Ctx) -> tuple[Any, Any]:
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            provider = provider_cache.get("provider")
            if provider is not None:
                return _acquire_from_provider(provider)
            resolver = _resolve_from_owner(ctx)
            provider = None
            if callable(resolver):
                provider = resolver(
                    router=getattr(ctx, "router", None) or getattr(ctx, "app", None),
                    model=model,
                    op_alias=alias if isinstance(alias, str) else None,
                )
            if provider is not None:
                provider_cache["provider"] = provider
                return _acquire_from_provider(provider)
            owner_session = _acquire_via_owner(ctx)
            if owner_session is not None:
                return owner_session
            raise RuntimeError("No runtime database acquisition callback is configured")

        self._db_acquire_cache[cache_key] = _acquire
        return _acquire

    async def _run_segment(self, ctx: _Ctx, packed: PackedKernel, seg_id: int) -> None:
        ctx.phase = normalize_phase(self._segment_phase_names(packed)[seg_id])
        await self._resolve_segment_runners(packed)[seg_id](ctx)

    async def _run_error_segments(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        *phase_names: str,
    ) -> None:
        seen: set[str] = set()
        for phase_name in phase_names:
            if phase_name in seen:
                continue
            seen.add(phase_name)
            for seg_id in error_phase_segments.get(phase_name, ()):
                try:
                    await self._run_segment(ctx, packed, seg_id)
                except Exception:
                    pass

    async def _run_rollback_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
    ) -> None:
        rollback_segments = error_phase_segments.get("TX_ROLLBACK", ())
        if rollback_segments:
            await self._run_error_segments(
                ctx,
                packed,
                error_phase_segments,
                "TX_ROLLBACK",
            )
            return

        db = getattr(ctx, "db", None) or getattr(ctx, "_raw_db", None)
        rollback = getattr(db, "rollback", None)
        if not callable(rollback):
            return
        rv = rollback()
        if inspect.isawaitable(rv):
            await rv

    async def _prepare_error_edge(
        self,
        ctx: _Ctx,
        packed: PackedKernel,
        error_phase_segments: Mapping[str, tuple[int, ...]],
        exc: BaseException,
    ) -> str:
        failed_phase = str(normalize_phase(getattr(ctx, "phase", "") or ""))
        rollback_required = failed_phase in {
            "START_TX",
            "PRE_HANDLER",
            "HANDLER",
            "POST_HANDLER",
            "PRE_COMMIT",
            "TX_COMMIT",
        } and bool(getattr(ctx, "owns_tx", False))
        edge = select_error_edge(
            failed_phase,
            rollback_required=rollback_required,
        )
        build_error_ctx(
            ctx,
            exc,
            failed_phase=failed_phase,
            err_target=edge.target,
            rollback_required=edge.target.kind == "rollback",
        )
        if edge.target.kind == "rollback":
            await self._run_rollback_edge(ctx, packed, error_phase_segments)
        return error_phase_for(failed_phase)

    def _resolve_error_segments(
        self,
        packed: PackedKernel,
        program_id: int,
    ) -> Mapping[str, tuple[int, ...]]:
        cache_key = (id(packed), program_id)
        cached = self._program_error_segments_cache.get(cache_key)
        if cached is not None:
            return cached[1]

        profile_ids = self._hot_array(
            packed,
            "program_error_profile_ids",
            tuple(getattr(packed, "program_error_profile_ids", ()) or ()),
        )
        profile_offsets = self._hot_array(
            packed,
            "error_profile_offsets",
            tuple(getattr(packed, "error_profile_offsets", ()) or ()),
        )
        if profile_offsets and program_id < len(profile_ids):
            phase_names = tuple(getattr(packed, "phase_names", ()) or ())
            profile_lengths = self._hot_array(packed, "error_profile_lengths", tuple(getattr(packed, "error_profile_lengths", ()) or ()))
            phase_ids = self._hot_array(packed, "error_profile_phase_ids", tuple(getattr(packed, "error_profile_phase_ids", ()) or ()))
            seg_ref_offsets = self._hot_array(packed, "error_profile_segment_offsets", tuple(getattr(packed, "error_profile_segment_ref_offsets", ()) or ()))
            seg_ref_lengths = self._hot_array(packed, "error_profile_segment_lengths", tuple(getattr(packed, "error_profile_segment_ref_lengths", ()) or ()))
            seg_refs = self._hot_array(packed, "error_profile_segment_refs", tuple(getattr(packed, "error_profile_segment_refs", ()) or ()))
            profile_id = profile_ids[program_id]
            if 0 <= profile_id < len(profile_offsets):
                start = profile_offsets[profile_id]
                length = profile_lengths[profile_id] if profile_id < len(profile_lengths) else 0
                frozen = {}
                for idx in range(start, start + length):
                    phase_id = phase_ids[idx]
                    phase_name = (
                        phase_names[phase_id]
                        if 0 <= phase_id < len(phase_names)
                        else str(phase_id)
                    )
                    seg_start = seg_ref_offsets[idx]
                    seg_length = seg_ref_lengths[idx]
                    frozen[str(normalize_phase(phase_name))] = tuple(
                        int(seg_refs[j]) for j in range(seg_start, seg_start + seg_length)
                    )
                ordered_segments, remaining_segments = self._resolve_segments_for_program(
                    packed, program_id
                )
                self._program_error_segments_cache[cache_key] = (
                    (*ordered_segments, *remaining_segments),
                    frozen,
                )
                return frozen

        grouped: dict[str, list[int]] = {}
        segment_offsets = self._hot_array(
            packed,
            "program_segment_offsets",
            tuple(getattr(packed, "program_segment_ref_offsets", ()) or getattr(packed, "op_segment_offsets", ()) or ()),
        )
        segment_lengths = self._hot_array(
            packed,
            "program_segment_lengths",
            tuple(getattr(packed, "program_segment_ref_lengths", ()) or getattr(packed, "op_segment_lengths", ()) or ()),
        )
        segment_refs = self._hot_array(
            packed,
            "program_segment_refs",
            tuple(getattr(packed, "program_segment_refs", ()) or getattr(packed, "op_to_segment_ids", ()) or ()),
        )
        segment_phases = self._segment_phase_names(packed)
        seg_offset = segment_offsets[program_id]
        seg_length = segment_lengths[program_id]
        for i in range(seg_offset, seg_offset + seg_length):
            seg_id = segment_refs[i]
            phase_name = str(normalize_phase(segment_phases[seg_id]))
            if phase_name.startswith("ON_") or phase_name == "TX_ROLLBACK":
                grouped.setdefault(phase_name, []).append(seg_id)

        ordered_segments, remaining_segments = self._resolve_segments_for_program(
            packed, program_id
        )
        frozen = {phase: tuple(seg_ids) for phase, seg_ids in grouped.items()}
        self._program_error_segments_cache[cache_key] = (
            (*ordered_segments, *remaining_segments),
            frozen,
        )
        return frozen

    async def _execute_packed(
        self, env: Any, ctx: _Ctx, plan: KernelPlan, packed: PackedKernel
    ) -> None:
        _send_json, _send_transport_response = self._resolve_transport_senders()
        StatusDetailError, create_standardized_error = self._resolve_error_helpers()

        temp = getattr(ctx, "temp", None)
        if not isinstance(temp, dict):
            ctx.temp = {}
            temp = ctx.temp

        hot = self._ensure_hot_ctx(ctx, env)
        ctx.plan = plan
        ctx.kernel_plan = plan
        if hot.method and getattr(ctx, "method", None) in (None, ""):
            ctx.method = hot.method
        if hot.path and getattr(ctx, "path", None) in (None, ""):
            ctx.path = hot.path

        program_id = self._require_program_id_from_ctx(ctx)
        if program_id < 0:
            program_id = self._prime_exact_route_program(ctx, env, packed)
        if program_id < 0:
            program_id = await self._probe_ingress_for_program(ctx, plan, packed)
        if program_id < 0:
            scope = getattr(env, "scope", {}) or {}
            egress = temp.get("egress") if isinstance(temp, dict) else None
            transport = (
                egress.get("transport_response") if isinstance(egress, dict) else None
            )
            if isinstance(transport, dict):
                await _send_transport_response(env, ctx)
                return

            route = temp.get("route", {})
            if isinstance(route, dict) and route.get("method_not_allowed") is True:
                await _send_json(env, 405, {"detail": "Method Not Allowed"})
                return
            if str(scope.get("type") or "") == "websocket":
                send = getattr(env, "send", None)
                if callable(send):
                    await send({"type": "websocket.close", "code": 4404})
                return
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return

        temp["program_id"] = program_id

        hot_op_plan = (
            packed.hot_op_plans[program_id]
            if program_id < len(getattr(packed, "hot_op_plans", ()))
            else None
        )

        if program_id >= len(plan.opmeta):
            await _send_json(
                env, 404, {"detail": "No runtime operation matched request."}
            )
            return
        if hot_op_plan is not None:
            ctx.model = hot_op_plan.model
            ctx.op = hot_op_plan.alias
            ctx.target = hot_op_plan.target
        else:
            meta = plan.opmeta[program_id]
            ctx.model = getattr(meta, "model", None)
            ctx.op = getattr(meta, "alias", None)
            ctx.target = getattr(meta, "target", None)
        env_ref = ctx.get("env")
        if env_ref is None:
            ctx["env"] = SimpleNamespace(method=ctx.op)
        elif getattr(env_ref, "method", None) in (None, "", "unknown"):
            try:
                setattr(env_ref, "method", ctx.op)
            except Exception:
                ctx["env"] = SimpleNamespace(method=ctx.op)
        release_db = None
        if getattr(ctx, "_raw_db", None) is None:
            try:
                acquire_db = self._resolve_db_acquire(plan, program_id, hot_op_plan)
                db, release_db = acquire_db(ctx)
                ctx._raw_db = db
                ctx.owns_tx = True
            except Exception:
                release_db = None
        if hot_op_plan is not None and hot_op_plan.opview is not None:
            ctx.opview = hot_op_plan.opview
        else:
            app = getattr(ctx, "app", None)
            if app is not None and ctx.model is not None and isinstance(ctx.op, str):
                opview_key = (id(plan), program_id)
                opview = self._opview_cache.get(opview_key)
                if opview is None:
                    opview = self.runtime.kernel.get_opview(app, ctx.model, ctx.op)
                    self._opview_cache[opview_key] = opview
                ctx.opview = opview

        try:
            if hot_op_plan is not None:
                error_phase_segments = hot_op_plan.error_segment_ids
            else:
                error_phase_segments = self._resolve_error_segments(
                    packed,
                    program_id,
                )

            try:
                await self._resolve_program_runner(
                    packed,
                    program_id,
                    hot_op_plan,
                )(ctx)
            except StatusDetailError as exc:
                detail = (
                    exc.detail
                    if getattr(exc, "detail", None) not in (None, "")
                    else str(exc)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(exc, "status_code", 500) or 500)
                payload = self._jsonrpc_error_payload(ctx, status_code, detail)
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(exc, "headers", None),
                )
                return
            except Exception as exc:
                std = create_standardized_error(exc)
                detail = (
                    std.detail
                    if getattr(std, "detail", None) not in (None, "")
                    else str(std)
                )
                error_phase = await self._prepare_error_edge(
                    ctx,
                    packed,
                    error_phase_segments,
                    exc,
                )
                fallback_phase = "ON_ERROR"
                await self._run_error_segments(
                    ctx,
                    packed,
                    error_phase_segments,
                    error_phase,
                    fallback_phase,
                )
                status_code = int(getattr(std, "status_code", 500) or 500)
                persistence_error = self._is_persistence_exception(exc)
                if persistence_error:
                    status_code = 500
                    detail = "Internal error"
                payload = self._jsonrpc_error_payload(
                    ctx,
                    status_code,
                    detail,
                    sanitize_detail=persistence_error,
                )
                await _send_json(
                    env,
                    200 if payload is not None else status_code,
                    payload or {"detail": detail},
                    headers=getattr(std, "headers", None),
                )
                return

            route = temp.get("route", {}) if isinstance(temp, dict) else {}
            egress = temp.get("egress", {}) if isinstance(temp, dict) else {}
            if isinstance(temp, dict) and temp.get("_tigrbl_hot_direct_create") is True:
                status = int(getattr(ctx, "status_code", 201) or 201)
                payload = self._serialize_model_row(getattr(ctx, "result", None))
                await _send_json(env, status, payload)
                return
            if (
                isinstance(route, dict)
                and route.get("short_circuit") is True
                and isinstance(egress, dict)
                and egress.get("transport_response")
            ):
                await _send_transport_response(env, ctx)
                return

            await _send_transport_response(env, ctx)
        finally:
            if callable(release_db):
                try:
                    release_db()
                except Exception:
                    pass

    def _build_python_packed_executor(self, packed: PackedKernel):
        async def _executor(kernel: Any, env: Any, ctx: _Ctx, plan: KernelPlan) -> None:
            del kernel
            await self._execute_packed(env, ctx, plan, packed)

        return _executor

    def _build_numba_packed_executor(self, packed: PackedKernel):
        if not packed.route_to_program:
            return None
        try:
            from numba import njit
        except Exception:
            return None

        route_to_program = packed.route_to_program

        @njit(cache=True)
        def _dispatch(proto_id: int, selector_id: int) -> int:
            if proto_id < 0 or selector_id < 0:
                return -1
            if proto_id >= len(route_to_program):
                return -1
            row = route_to_program[proto_id]
            if selector_id >= len(row):
                return -1
            return row[selector_id]

        def _executor(proto_id: int, selector_id: int) -> int:
            return int(_dispatch(int(proto_id), int(selector_id)))

        return _executor

    async def invoke(
        self,
        *,
        runtime: Any,
        env: Any,
        ctx: Any,
        plan: Any,
        packed_plan: Any | None = None,
    ) -> Any:
        if not isinstance(plan, KernelPlan):
            raise TypeError("PackedPlanExecutor requires a KernelPlan instance")
        if not isinstance(packed_plan, PackedKernel):
            raise TypeError("PackedPlanExecutor requires a PackedKernel instance")

        base_ctx = _Ctx.ensure(
            request=ctx.get("request") if isinstance(ctx, Mapping) else None,
            db=ctx.get("db") if isinstance(ctx, Mapping) else None,
            seed=ctx,
        )
        await self._execute_packed(env, base_ctx, plan, packed_plan)
        return base_ctx.get("result")


__all__ = ["PackedPlanExecutor"]
