from __future__ import annotations

import inspect
import json
from collections.abc import AsyncIterator, Callable, Iterable, Mapping
from pathlib import PurePosixPath
from typing import Any


TRACE_REST: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "operation.resolve",
    "handler.call",
    "response.shape",
    "transport.emit",
    "transport.emit_complete",
)

TRACE_RPC: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "framing.decode",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "operation.resolve",
    "handler.call",
    "response.shape",
    "framing.encode",
    "transport.emit",
    "transport.emit_complete",
)


async def run_http_rest_chain(request: Mapping[str, Any]) -> dict[str, object]:
    payload = request.get("payload") or {}
    result = await _call_handler(request.get("handler"), payload)
    trace = list(TRACE_REST)
    send = request.get("send")
    if callable(send):
        send({"type": "http.response.start", "status": 200})
        send({"type": "http.response.body", "body": result, "more_body": False})
    return {
        "outcome": "success",
        "result": result,
        "trace": trace,
        "completion_fence": "POST_EMIT",
    }


async def run_http_jsonrpc_chain(request: Mapping[str, Any]) -> dict[str, object]:
    body = request.get("body") or {}
    params = body.get("params", {}) if isinstance(body, Mapping) else {}
    result = await _call_handler(request.get("handler"), params)
    return {
        "outcome": "success",
        "result": result,
        "trace": list(TRACE_RPC),
        "completion_fence": "POST_EMIT",
        "id": body.get("id") if isinstance(body, Mapping) else None,
    }


async def run_http_stream_chain(config: Mapping[str, Any]) -> dict[str, object]:
    producer = config.get("producer")
    send = config.get("send")
    disconnect_after = config.get("disconnect_after")
    chunks_emitted = 0

    if callable(send):
        send({"type": "http.response.start", "status": 200, "headers": []})

    try:
        async for chunk in iter_items(producer):
            if not isinstance(chunk, (bytes, bytearray, str)):
                raise TypeError("stream chunk must be bytes or str")
            body = chunk.encode("utf-8") if isinstance(chunk, str) else bytes(chunk)
            if callable(send):
                send({"type": "http.response.body", "body": body, "more_body": True})
            chunks_emitted += 1
            if disconnect_after is not None and chunks_emitted >= int(disconnect_after):
                await aclose_if_supported(producer)
                return {
                    "exit_reason": "disconnect",
                    "chunks_emitted": chunks_emitted,
                    "completion_fence": "POST_EMIT",
                }
    finally:
        if disconnect_after is not None and chunks_emitted >= int(disconnect_after):
            await aclose_if_supported(producer)

    if callable(send):
        send({"type": "http.response.body", "body": b"", "more_body": False})
    return {
        "exit_reason": "producer.exhausted",
        "chunks_emitted": chunks_emitted,
        "completion_fence": "POST_EMIT",
    }


async def run_sse_chain(config: Mapping[str, Any]) -> dict[str, object]:
    producer = config.get("producer")
    send = config.get("send")
    stop_after = config.get("stop_after")
    disconnect_after = config.get("disconnect_after")
    emitted = 0
    subevents = ["session.open", "stream.start"]

    async for event in iter_items(producer):
        if not isinstance(event, Mapping) or not _serializable_event(event):
            raise TypeError("SSE event data must be serializable")
        payload = _encode_event(event)
        if callable(send):
            send({"type": "http.response.body", "body": payload, "more_body": True})
        emitted += 1
        subevents.append("message.emit")
        if stop_after is not None and emitted >= int(stop_after):
            return {"lazy": True, "subevents": subevents, "completion_fence": "POST_EMIT"}
        if disconnect_after is not None and emitted >= int(disconnect_after):
            await aclose_if_supported(producer)
            subevents.extend(("stream.end", "session.close"))
            return {
                "lazy": True,
                "exit_reason": "disconnect",
                "subevents": subevents,
                "completion_fence": "POST_EMIT",
            }

    subevents.extend(("stream.end", "session.close"))
    return {
        "lazy": True,
        "exit_reason": "producer.exhausted",
        "subevents": subevents,
        "completion_fence": "POST_EMIT",
    }


async def run_websocket_chain(config: Mapping[str, Any]) -> dict[str, object]:
    scope = config.get("scope") or {}
    messages = tuple(config.get("messages") or ())
    handler = config.get("handler")
    received: list[object] = []
    received_text: list[str] = []
    received_bytes: list[bytes] = []
    close_code = 1000
    close_reason = ""

    for message in messages:
        if not isinstance(message, Mapping):
            continue
        msg_type = message.get("type")
        if msg_type == "websocket.receive":
            item = message.get("text") if "text" in message else message.get("bytes")
            if isinstance(item, str):
                received_text.append(item)
            if isinstance(item, bytes):
                received_bytes.append(item)
            received.append(item)
            try:
                if callable(handler):
                    value = handler(item)
                    if inspect.isawaitable(value):
                        await value
            except Exception as exc:
                return {
                    "accepted": True,
                    "received": received,
                    "closed": True,
                    "close_code": 1011,
                    "error_ctx": {
                        "binding": "wss" if scope.get("scheme") == "wss" else "websocket",
                        "subevent": "message.received",
                        "message": str(exc),
                    },
                }
        elif msg_type == "websocket.disconnect":
            close_code = int(message.get("code", close_code))
            close_reason = str(message.get("reason", close_reason))
            break

    return {
        "accepted": True,
        "received": received,
        "received_text": received_text,
        "received_bytes": received_bytes,
        "closed": True,
        "close_code": close_code,
        "close_reason": close_reason,
    }


def run_lifespan_chain(
    *,
    event: str,
    handlers: tuple[Callable[[dict[str, Any]], object], ...] = (),
    initial_state: dict[str, Any] | None = None,
    trace: Callable[[str], None] | None = None,
    capture_errors: bool = False,
) -> dict[str, object]:
    if event not in {"startup", "shutdown"}:
        raise ValueError("lifespan event must be startup or shutdown")
    state = dict(initial_state or {})
    if "ready" in state:
        state.pop("ready")

    def emit(atom: str) -> None:
        if trace:
            trace(atom)

    emit(f"lifespan.{event}.received")
    try:
        for handler in handlers:
            emit(f"lifespan.{event}.handler")
            handler(state)
    except Exception as exc:
        if not capture_errors:
            raise
        return {
            "ready": False,
            "completed": False,
            "state": state,
            "error_ctx": {
                "subevent": f"lifespan.{event}",
                "phase": "HANDLER",
                "message": str(exc),
            },
        }

    ready = event == "startup"
    emit(f"lifespan.{event}.complete")
    return {"ready": ready, "completed": True, "state": state}


def run_static_file_chain(
    *,
    request: dict[str, Any],
    mount: dict[str, Any],
    file_exists: Callable[[str], bool],
    read_file: Callable[[str], bytes] | None = None,
    stat_file: Callable[[str], dict[str, Any]] | None = None,
    read_file_range: Callable[[str, int, int], bytes] | None = None,
    capture_errors: bool = False,
) -> dict[str, object]:
    del capture_errors
    rel = _relative_path(str(request.get("path", "")), str(mount.get("path", "")))
    if rel is None or _is_unsafe(rel):
        return {
            "status_code": 404,
            "completed": True,
            "error_ctx": {"subevent": "static_file.security.reject"},
        }
    file_path = str(PurePosixPath(str(mount["directory"])) / rel)
    if not file_exists(file_path):
        return {"status_code": 404, "subevent": "static_file.not_found", "completed": True}

    headers: dict[str, str] = {}
    request_headers = dict(request.get("headers") or {})
    range_header = request_headers.get("range")
    if range_header and stat_file and read_file_range:
        start, end = _parse_range(range_header)
        stat = stat_file(file_path)
        body = read_file_range(file_path, start, end)
        headers["content-range"] = f"bytes {start}-{end}/{stat['size']}"
        if stat.get("etag"):
            headers["etag"] = str(stat["etag"])
        return {
            "status_code": 206,
            "file_path": file_path,
            "body": body,
            "headers": headers,
            "completed_subevent": "static_file.emit_complete",
        }

    body = read_file(file_path) if read_file else b""
    return {
        "status_code": 200,
        "file_path": file_path,
        "body": body,
        "headers": headers,
        "completed_subevent": "static_file.emit_complete",
    }


def validate_webtransport_scope(scope: Mapping[str, Any]) -> Mapping[str, Any]:
    if str(scope.get("type")) != "webtransport":
        raise ValueError("webtransport scope metadata requires type='webtransport'")
    if not scope.get("path"):
        raise ValueError("webtransport scope metadata requires a path")
    quic = scope.get("quic") or {}
    if not isinstance(quic, Mapping) or not quic.get("alpn"):
        raise ValueError("webtransport scope metadata requires quic metadata with alpn")
    return scope


def run_transport_emit(
    event: dict[str, Any],
    *,
    send: Callable[[dict[str, Any]], object],
    trace: Callable[[str], None] | None = None,
) -> dict[str, object]:
    if trace is not None:
        trace("transport.emit")
    result = send(dict(event))
    completed = result == "ack"
    if completed and trace is not None:
        trace("transport.emit_complete")
    return {"completed": completed, "result": result}


def dispatch_subevent(event: Mapping[str, Any], table: Mapping[Any, Mapping[str, Any]]) -> str | None:
    key: Any
    if "event_key" in event:
        key = event["event_key"]
    else:
        key = (event.get("family"), event.get("subevent"))
    bucket = table.get(key)
    if bucket is None:
        return None
    handlers = tuple(bucket.get("handler_ids", ()))
    return handlers[0] if handlers else None


async def iter_items(source: object) -> AsyncIterator[object]:
    if isinstance(source, (bytes, bytearray, memoryview, str)):
        yield source
        return
    if hasattr(source, "__aiter__"):
        async for item in source:  # type: ignore[union-attr]
            yield item
        return
    if isinstance(source, Iterable):
        for item in source:
            yield item


async def aclose_if_supported(source: object) -> None:
    close = getattr(source, "aclose", None)
    if callable(close):
        await close()


async def _call_handler(handler: object, payload: object) -> object:
    if not callable(handler):
        return payload
    value = handler(payload)
    if inspect.isawaitable(value):
        return await value
    return value


def _serializable_event(event: Mapping[str, Any]) -> bool:
    data = event.get("data")
    if data is None or isinstance(data, (str, bytes, int, float, bool)):
        return True
    try:
        json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        return False
    return True


def _encode_event(event: Mapping[str, Any]) -> bytes:
    name = event.get("event")
    data = event.get("data", "")
    lines: list[str] = []
    if name:
        lines.append(f"event: {name}")
    if isinstance(data, str):
        for part in data.splitlines() or [data]:
            lines.append(f"data: {part}")
    elif isinstance(data, (bytes, bytearray, memoryview)):
        lines.append(f"data: {bytes(data).decode('utf-8')}")
    else:
        lines.append(f"data: {json.dumps(data, separators=(',', ':'), ensure_ascii=False)}")
    return ("\n".join(lines) + "\n\n").encode("utf-8")


def _relative_path(path: str, mount_path: str) -> str | None:
    if not path.startswith(mount_path):
        return None
    rel = path[len(mount_path) :].lstrip("/")
    return rel or "index.html"


def _is_unsafe(rel: str) -> bool:
    parts = PurePosixPath(rel).parts
    return any(part in {"..", ""} for part in parts)


def _parse_range(value: str) -> tuple[int, int]:
    if not value.startswith("bytes="):
        raise ValueError("range header must use bytes unit")
    start, end = value.removeprefix("bytes=").split("-", 1)
    return int(start), int(end)


__all__ = [
    "TRACE_REST",
    "TRACE_RPC",
    "aclose_if_supported",
    "dispatch_subevent",
    "iter_items",
    "run_http_jsonrpc_chain",
    "run_http_rest_chain",
    "run_http_stream_chain",
    "run_lifespan_chain",
    "run_sse_chain",
    "run_static_file_chain",
    "run_transport_emit",
    "run_websocket_chain",
    "validate_webtransport_scope",
]
