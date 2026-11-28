from __future__ import annotations

from typing import Any

_BINDINGS = {
    "http.rest": ("request_response", "request_response", "request.received"),
    "http.jsonrpc": ("request_response", "rpc", "rpc.request"),
    "http.stream": ("server_stream", "stream", "stream.start"),
    "http.sse": ("server_stream", "event_stream", "message.emit"),
    "websocket": ("bidirectional_stream", "socket", "message.received"),
    "ws": ("bidirectional_stream", "socket", "message.received"),
}


def derive_runtime_event(event: dict[str, Any]) -> dict[str, Any]:
    subevent = event.get("subevent")
    if isinstance(subevent, str) and "." not in subevent:
        raise ValueError("subevent must be qualified, for example request.received")
    binding = str(event.get("binding", ""))
    try:
        exchange, family, default_subevent = _BINDINGS[binding]
    except KeyError as exc:
        raise ValueError(
            f"unsupported binding for exchange/subevent dispatch: {binding}"
        ) from exc
    return {
        **event,
        "binding": binding,
        "exchange": exchange,
        "family": family,
        "subevent": subevent or default_subevent,
    }


def resolve_operation(metadata: dict[str, Any]) -> dict[str, Any]:
    binding = str(metadata.get("binding", ""))
    subevent = str(metadata.get("subevent", ""))
    method = str(metadata.get("method", metadata.get("path", "")))
    return {
        "exchange": metadata["exchange"],
        "family": metadata["family"],
        "subevent": subevent,
        "op_code": f"{binding}:{subevent}:{method}".strip(":"),
    }


__all__ = ["derive_runtime_event", "resolve_operation"]
