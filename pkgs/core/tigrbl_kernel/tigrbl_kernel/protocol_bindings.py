from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _unsupported(message: str) -> ValueError:
    return ValueError(f"binding protocol unsupported before runtime: {message}")


def compile_binding_protocol_plan(op_id: str, binding: Mapping[str, Any]) -> dict[str, object]:
    kind = binding.get("kind")
    if not kind:
        raise ValueError(
            "BindingSpec binding source is required; transport guessing is ambiguous"
        )

    kind = str(kind)
    framing = binding.get("framing")
    rows: tuple[dict[str, str], ...]

    if kind == "http.rest":
        if framing not in (None, "json"):
            raise _unsupported("http.rest only supports json framing")
        family = "response"
        framing = "json"
        anchors = (
            "ingress.receive",
            "dispatch.subevent.derive",
            "handler.invoke",
            "transport.emit_complete",
        )
        rows = (
            {"family": "response", "subevent": "request.received"},
            {"family": "response", "subevent": "response.emit"},
        )
    elif kind == "http.jsonrpc":
        if not binding.get("rpc_method"):
            raise _unsupported("http.jsonrpc requires rpc_method")
        family = "response"
        framing = "jsonrpc"
        anchors = (
            "framing.decode",
            "dispatch.subevent.derive",
            "handler.invoke",
            "framing.encode",
        )
        rows = (
            {"family": "response", "subevent": "request.received"},
            {"family": "response", "subevent": "response.emit"},
        )
    elif kind == "http.stream":
        family = "stream"
        framing = "stream"
        anchors = ("handler.invoke", "transport.emit", "transport.emit_complete")
        rows = (
            {"family": "stream", "subevent": "stream.chunk"},
            {"family": "stream", "subevent": "stream.close"},
        )
    elif kind == "http.sse":
        family = "stream"
        framing = "sse"
        anchors = (
            "framing.encode",
            "handler.invoke",
            "transport.emit",
            "transport.emit_complete",
        )
        rows = (
            {"family": "event_stream", "subevent": "message.encoded"},
            {"family": "event_stream", "subevent": "message.emit"},
            {"family": "stream", "subevent": "stream.close"},
        )
    elif kind in {"ws", "websocket"}:
        if binding.get("methods"):
            raise _unsupported("websocket bindings do not accept HTTP methods")
        family = "message"
        framing = str(framing or "text")
        anchors = (
            "transport.accept",
            "framing.decode",
            "dispatch.subevent.derive",
            "handler.invoke",
            "transport.close",
        )
        rows = (
            {"family": "message", "subevent": "message.received"},
            {"family": "message", "subevent": "message.emit"},
            {"family": "session", "subevent": "session.close"},
        )
    elif kind == "webtransport":
        if binding.get("exchange") == "request_response":
            raise _unsupported("webtransport request_response exchange")
        family = "session"
        framing = "webtransport"
        anchors = (
            "transport.accept",
            "dispatch.subevent.derive",
            "handler.invoke",
            "transport.close",
        )
        rows = (
            {"family": "session", "subevent": "session.open"},
            {"family": "session", "subevent": "session.close"},
        )
    else:
        raise _unsupported(kind)

    return {
        "op_id": op_id,
        "binding_kind": kind,
        "family": family,
        "framing": framing,
        "atom_anchors": anchors,
        "event_key_inputs": {
            "family": family,
            "binding": kind,
            "framing": framing,
        },
        "capability_requirements": {
            "required_mask": _required_mask(kind=kind, family=family, framing=str(framing)),
        },
        "lifecycle_rows": rows,
    }


def _required_mask(*, kind: str, family: str, framing: str) -> int:
    source = f"{kind}:{family}:{framing}".encode("utf-8")
    value = 0
    for byte in source:
        value = ((value << 5) ^ byte) & 0xFFFF_FFFF
    return value


__all__ = ["compile_binding_protocol_plan"]
