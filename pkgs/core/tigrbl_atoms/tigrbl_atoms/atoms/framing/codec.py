from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from tigrbl_core._spec.binding_spec import validate_webtransport_inner_framing

_BYTES_TYPES = (bytes, bytearray, memoryview)
_WEBSOCKET_FRAME_TYPES = {"websocket.receive", "websocket.send"}


@dataclass(frozen=True)
class FrameCodec:
    name: str
    encode: Any | None
    decode: Any | None

    @property
    def supports_encode(self) -> bool:
        return self.encode is not None

    @property
    def supports_decode(self) -> bool:
        return self.decode is not None


def _loads(raw: bytes | bytearray | str, framing: str) -> Any:
    try:
        text = _as_text(raw, framing)
        return json.loads(text)
    except Exception as exc:
        raise ValueError(f"invalid {framing} framing decode payload") from exc


def _dumps(payload: Any) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode("utf-8")


def _as_text(raw: Any, framing: str) -> str:
    if isinstance(raw, str):
        return raw
    if isinstance(raw, _BYTES_TYPES):
        try:
            return bytes(raw).decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"invalid {framing} framing decode payload") from exc
    raise ValueError(f"invalid {framing} framing decode payload")


def _as_bytes(raw: Any, framing: str) -> bytes:
    if isinstance(raw, _BYTES_TYPES):
        return bytes(raw)
    raise ValueError(f"invalid {framing} framing payload")


def _websocket_body(payload: Any, framing: str) -> Any:
    if not isinstance(payload, Mapping):
        return payload
    message_type = payload.get("type")
    if message_type is not None and message_type not in _WEBSOCKET_FRAME_TYPES:
        raise ValueError(f"invalid {framing} framing decode payload")
    if "text" in payload:
        return payload["text"]
    if "bytes" in payload:
        return payload["bytes"]
    raise ValueError(f"invalid {framing} framing decode payload")


def _valid_jsonrpc_id(value: Any) -> bool:
    return value is None or (
        not isinstance(value, bool) and isinstance(value, (int, str))
    )


def _validate_jsonrpc_error(error: Any) -> None:
    if not isinstance(error, Mapping):
        raise ValueError("invalid jsonrpc framing payload")
    code = error.get("code")
    message = error.get("message")
    if isinstance(code, bool) or not isinstance(code, int) or not isinstance(message, str):
        raise ValueError("invalid jsonrpc framing payload")


def _validate_jsonrpc_object(message: Any) -> None:
    if not isinstance(message, Mapping) or message.get("jsonrpc") != "2.0":
        raise ValueError("invalid jsonrpc framing payload")

    has_method = "method" in message
    has_result = "result" in message
    has_error = "error" in message

    if has_method:
        method = message.get("method")
        if not isinstance(method, str) or not method or has_result or has_error:
            raise ValueError("invalid jsonrpc framing payload")
        if "id" in message and not _valid_jsonrpc_id(message["id"]):
            raise ValueError("invalid jsonrpc framing payload")
        return

    if has_result == has_error or "id" not in message:
        raise ValueError("invalid jsonrpc framing payload")
    if not _valid_jsonrpc_id(message["id"]):
        raise ValueError("invalid jsonrpc framing payload")
    if has_error:
        _validate_jsonrpc_error(message["error"])


def _validate_jsonrpc_payload(data: Any) -> Any:
    if isinstance(data, list):
        if not data:
            raise ValueError("invalid jsonrpc framing payload")
        for message in data:
            _validate_jsonrpc_object(message)
        return data
    _validate_jsonrpc_object(data)
    return data


def _prepare_jsonrpc_payload(payload: Any) -> dict[str, Any] | list[dict[str, Any]]:
    if isinstance(payload, Mapping):
        body = dict(payload)
        body.setdefault("jsonrpc", "2.0")
        _validate_jsonrpc_object(body)
        return body
    if isinstance(payload, Iterable) and not isinstance(payload, (str, *_BYTES_TYPES)):
        batch: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, Mapping):
                raise ValueError("invalid jsonrpc framing payload")
            body = dict(item)
            body.setdefault("jsonrpc", "2.0")
            _validate_jsonrpc_object(body)
            batch.append(body)
        if not batch:
            raise ValueError("invalid jsonrpc framing payload")
        return batch
    raise ValueError("invalid jsonrpc framing payload")


def _decode_ndjson(payload: Any, framing: str) -> list[Any]:
    text = _as_text(payload, framing)
    if text == "":
        return []
    records: list[Any] = []
    for line in text.splitlines():
        if not line.strip():
            raise ValueError(f"invalid {framing} framing decode payload")
        try:
            records.append(json.loads(line))
        except Exception as exc:
            raise ValueError(f"invalid {framing} framing decode payload") from exc
    return records


def _encode_ndjson(payload: Any) -> bytes:
    if isinstance(payload, Mapping) or isinstance(payload, (str, *_BYTES_TYPES)):
        raise ValueError("invalid ndjson framing payload")
    if not isinstance(payload, Iterable):
        raise ValueError("invalid ndjson framing payload")
    return b"".join(_dumps(record) + b"\n" for record in payload)


def _websocket_text_message(text: str) -> dict[str, Any]:
    return {"type": "websocket.send", "text": text}


def _websocket_bytes_message(payload: bytes) -> dict[str, Any]:
    return {"type": "websocket.send", "bytes": payload}


def _decode_json(payload: Any) -> Any:
    return _loads(payload, "json")


def _decode_jsonrpc(payload: Any) -> Any:
    data = _loads(payload, "jsonrpc")
    return _validate_jsonrpc_payload(data)


def _decode_ndjson_frame(payload: Any) -> list[Any]:
    return _decode_ndjson(payload, "ndjson")


def _decode_text(payload: Any) -> str:
    return _as_text(payload, "text")


def _decode_bytes(payload: Any) -> bytes:
    return _as_bytes(payload, "bytes")


def _decode_binary(payload: Any) -> bytes:
    return _as_bytes(payload, "binary")


def _decode_stream(payload: Any) -> bytes:
    return _as_bytes(payload, "stream")


def _decode_websocket_text(payload: Any) -> str:
    return _as_text(_websocket_body(payload, "websocket.text"), "websocket.text")


def _decode_websocket_json(payload: Any) -> Any:
    return _loads(_websocket_body(payload, "websocket.json"), "websocket.json")


def _decode_websocket_jsonrpc(payload: Any) -> Any:
    data = _loads(_websocket_body(payload, "websocket.jsonrpc"), "websocket.jsonrpc")
    return _validate_jsonrpc_payload(data)


def _decode_websocket_ndjson(payload: Any) -> list[Any]:
    return _decode_ndjson(_websocket_body(payload, "websocket.ndjson"), "websocket.ndjson")


def _decode_websocket_bytes(payload: Any) -> bytes:
    return _as_bytes(_websocket_body(payload, "websocket.bytes"), "websocket.bytes")


def _decode_websocket_binary(payload: Any) -> bytes:
    return _as_bytes(_websocket_body(payload, "websocket.binary"), "websocket.binary")


def _encode_json(payload: Any) -> bytes:
    return _dumps(payload)


def _encode_jsonrpc(payload: Any) -> bytes:
    return _dumps(_prepare_jsonrpc_payload(payload))


def _encode_ndjson_frame(payload: Any) -> bytes:
    return _encode_ndjson(payload)


def _encode_text(payload: Any) -> bytes:
    return payload.encode("utf-8") if isinstance(payload, str) else str(payload).encode("utf-8")


def _encode_bytes(payload: Any) -> bytes:
    return _as_bytes(payload, "bytes")


def _encode_binary(payload: Any) -> bytes:
    return _as_bytes(payload, "binary")


def _encode_stream(payload: Any) -> bytes:
    return _as_bytes(payload, "stream")


def _encode_sse(payload: Any) -> bytes:
    lines: list[str] = []
    for key in ("event", "id", "retry", "data"):
        if key in payload:
            lines.append(f"{key}: {payload[key]}")
    return ("\n".join(lines) + "\n\n").encode("utf-8")


def _encode_websocket_text(payload: Any) -> dict[str, Any]:
    text = payload["text"] if isinstance(payload, dict) else str(payload)
    return _websocket_text_message(text)


def _encode_websocket_json(payload: Any) -> dict[str, Any]:
    return _websocket_text_message(_dumps(payload).decode("utf-8"))


def _encode_websocket_jsonrpc(payload: Any) -> dict[str, Any]:
    return _websocket_text_message(
        _dumps(_prepare_jsonrpc_payload(payload)).decode("utf-8")
    )


def _encode_websocket_ndjson(payload: Any) -> dict[str, Any]:
    return _websocket_text_message(_encode_ndjson(payload).decode("utf-8"))


def _encode_websocket_bytes(payload: Any) -> dict[str, Any]:
    return _websocket_bytes_message(_as_bytes(payload, "websocket.bytes"))


def _encode_websocket_binary(payload: Any) -> dict[str, Any]:
    return _websocket_bytes_message(_as_bytes(payload, "websocket.binary"))


FRAME_CODECS: dict[str, FrameCodec] = {
    "json": FrameCodec("json", _encode_json, _decode_json),
    "jsonrpc": FrameCodec("jsonrpc", _encode_jsonrpc, _decode_jsonrpc),
    "ndjson": FrameCodec("ndjson", _encode_ndjson_frame, _decode_ndjson_frame),
    "text": FrameCodec("text", _encode_text, _decode_text),
    "bytes": FrameCodec("bytes", _encode_bytes, _decode_bytes),
    "binary": FrameCodec("binary", _encode_binary, _decode_binary),
    "stream": FrameCodec("stream", _encode_stream, _decode_stream),
    "sse": FrameCodec("sse", _encode_sse, None),
    "websocket.text": FrameCodec(
        "websocket.text",
        _encode_websocket_text,
        _decode_websocket_text,
    ),
    "websocket.json": FrameCodec(
        "websocket.json",
        _encode_websocket_json,
        _decode_websocket_json,
    ),
    "websocket.jsonrpc": FrameCodec(
        "websocket.jsonrpc",
        _encode_websocket_jsonrpc,
        _decode_websocket_jsonrpc,
    ),
    "websocket.ndjson": FrameCodec(
        "websocket.ndjson",
        _encode_websocket_ndjson,
        _decode_websocket_ndjson,
    ),
    "websocket.bytes": FrameCodec(
        "websocket.bytes",
        _encode_websocket_bytes,
        _decode_websocket_bytes,
    ),
    "websocket.binary": FrameCodec(
        "websocket.binary",
        _encode_websocket_binary,
        _decode_websocket_binary,
    ),
}


def get_frame_codec(framing: str) -> FrameCodec:
    try:
        return FRAME_CODECS[framing]
    except KeyError as exc:
        raise ValueError(f"unsupported framing kind: {framing}") from exc


def supported_frame_codecs() -> tuple[str, ...]:
    return tuple(FRAME_CODECS)


def decode_frame(framing: str, payload: bytes | bytearray | str) -> Any:
    codec = get_frame_codec(framing)
    if codec.decode is None:
        raise ValueError(f"unsupported framing decode kind: {framing}")
    return codec.decode(payload)


def encode_frame(framing: str, payload: Any) -> Any:
    codec = get_frame_codec(framing)
    if codec.encode is None:
        raise ValueError(f"unsupported framing encode kind: {framing}")
    return codec.encode(payload)


def encode_webtransport_inner_frame(
    *,
    lane: str,
    framing: str | None,
    payload: Any,
) -> bytes:
    selected = validate_webtransport_inner_framing(lane=lane, inner_framing=framing)
    if selected is None:
        return _as_bytes(payload, "webtransport")
    return encode_frame(selected, payload)


def decode_webtransport_inner_frame(
    *,
    lane: str,
    framing: str | None,
    payload: bytes | bytearray | str,
) -> Any:
    selected = validate_webtransport_inner_framing(lane=lane, inner_framing=framing)
    if selected is None:
        return _as_bytes(payload, "webtransport")
    return decode_frame(selected, payload)


__all__ = [
    "decode_frame",
    "decode_webtransport_inner_frame",
    "encode_frame",
    "encode_webtransport_inner_frame",
    "FrameCodec",
    "FRAME_CODECS",
    "get_frame_codec",
    "supported_frame_codecs",
]
