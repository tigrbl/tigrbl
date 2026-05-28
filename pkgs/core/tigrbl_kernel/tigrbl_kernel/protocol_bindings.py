from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tigrbl_core._spec.binding_spec import (
    validate_app_framing_for_binding,
    validate_webtransport_inner_framing,
    validate_webtransport_lane_exchange,
    webtransport_lane_for_profile,
    webtransport_runtime_family,
)


def _unsupported(message: str) -> ValueError:
    return ValueError(f"binding protocol unsupported before runtime: {message}")


def compile_binding_protocol_plan(op_id: str, binding: Mapping[str, Any]) -> dict[str, object]:
    kind = binding.get("kind") or binding.get("proto")
    if not kind:
        raise ValueError(
            "BindingSpec binding source is required; transport guessing is ambiguous"
        )

    kind = str(kind)
    profile = binding.get("profile")
    if kind in {"http", "https"} and profile:
        kind = f"{kind}.{profile}"
    elif kind == "websocket":
        kind = str(binding.get("proto") or "ws")
    framing = binding.get("framing")
    rows: tuple[dict[str, str], ...]

    if kind in {"http.rest", "https.rest"}:
        validate_app_framing_for_binding(binding_kind=kind, framing=str(framing or "json"))
        family = "request"
        framing = "json"
        anchors = (
            "ingress.receive",
            "dispatch.subevent.derive",
            "handler.invoke",
            "transport.emit_complete",
        )
        rows = (
            {"family": "request", "subevent": "request.received"},
            {"family": "request", "subevent": "response.emit"},
        )
    elif kind in {"http.jsonrpc", "https.jsonrpc"}:
        if not binding.get("rpc_method"):
            raise _unsupported("http.jsonrpc requires rpc_method")
        validate_app_framing_for_binding(binding_kind=kind, framing=str(framing or "jsonrpc"))
        family = "request"
        framing = "jsonrpc"
        anchors = (
            "framing.decode",
            "dispatch.subevent.derive",
            "handler.invoke",
            "framing.encode",
        )
        rows = (
            {"family": "request", "subevent": "request.received"},
            {"family": "request", "subevent": "response.emit"},
        )
    elif kind in {"http.stream", "https.stream"}:
        validate_app_framing_for_binding(binding_kind=kind, framing=str(framing or "stream"))
        family = "stream"
        framing = str(framing or "stream")
        anchors = ("handler.invoke", "transport.emit", "transport.emit_complete")
        rows = (
            {"family": "stream", "subevent": "stream.chunk"},
            {"family": "stream", "subevent": "stream.close"},
        )
    elif kind in {"http.sse", "https.sse"}:
        validate_app_framing_for_binding(binding_kind=kind, framing=str(framing or "sse"))
        family = "stream"
        framing = "sse"
        anchors = (
            "framing.encode",
            "handler.invoke",
            "transport.emit",
            "transport.emit_complete",
        )
        rows = (
            {"family": "stream", "subevent": "message.encoded"},
            {"family": "stream", "subevent": "message.emit"},
            {"family": "stream", "subevent": "stream.close"},
        )
    elif kind in {"ws", "wss", "websocket"}:
        if binding.get("methods"):
            raise _unsupported("websocket bindings do not accept HTTP methods")
        family = "message"
        framing = str(framing or "text")
        subprotocols = tuple(str(item).lower() for item in binding.get("subprotocols", ()))
        validate_app_framing_for_binding(
            binding_kind="wss" if kind == "wss" else "ws",
            framing=framing,
            subprotocols=subprotocols,
        )
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
        validate_app_framing_for_binding(binding_kind=kind, framing=str(framing or "webtransport"))
        if framing and str(framing) != "webtransport":
            raise _unsupported("webtransport outer framing must remain webtransport")
        lane = webtransport_lane_for_profile(
            binding.get("lane") or binding.get("profile") or "webtransport"
        )
        validate_webtransport_lane_exchange(
            lane=lane,
            exchange=str(binding.get("exchange") or {
                "session": "bidirectional_stream",
                "bidi_stream": "bidirectional_stream",
                "unidi_client_stream": "client_stream",
                "unidi_server_stream": "server_stream",
                "datagram": "bidirectional_stream",
            }[lane]),
        )
        inner_framing = validate_webtransport_inner_framing(
            lane=lane,
            inner_framing=binding.get("inner_framing"),
        )
        family = webtransport_runtime_family(lane)
        framing = "webtransport"
        if lane == "session":
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
        elif lane == "bidi_stream":
            anchors = (
                "transport.accept",
                "transport.receive",
                "framing.decode",
                "dispatch.subevent.derive",
                "handler.invoke",
                "framing.encode",
                "transport.emit",
                "transport.close",
            )
            rows = (
                {"family": "stream", "subevent": "stream.open"},
                {"family": "stream", "subevent": "stream.chunk.received"},
                {"family": "stream", "subevent": "stream.chunk.emit"},
                {"family": "stream", "subevent": "stream.close"},
            )
        elif lane == "unidi_client_stream":
            anchors = (
                "transport.accept",
                "transport.receive",
                "framing.decode",
                "dispatch.subevent.derive",
                "handler.invoke",
                "transport.close",
            )
            rows = (
                {"family": "stream", "subevent": "stream.open"},
                {"family": "stream", "subevent": "stream.chunk.received"},
                {"family": "stream", "subevent": "stream.close"},
            )
        elif lane == "unidi_server_stream":
            anchors = (
                "transport.accept",
                "handler.invoke",
                "framing.encode",
                "transport.emit",
                "transport.close",
            )
            rows = (
                {"family": "stream", "subevent": "stream.open"},
                {"family": "stream", "subevent": "stream.chunk.emit"},
                {"family": "stream", "subevent": "stream.emit_complete"},
                {"family": "stream", "subevent": "stream.close"},
            )
        elif lane == "datagram":
            anchors = (
                "transport.accept",
                "transport.receive",
                "framing.decode",
                "dispatch.subevent.derive",
                "handler.invoke",
                "framing.encode",
                "transport.emit",
            )
            rows = (
                {"family": "datagram", "subevent": "datagram.received"},
                {"family": "datagram", "subevent": "datagram.emit"},
                {"family": "datagram", "subevent": "datagram.emit_complete"},
            )
        else:  # pragma: no cover - guarded by webtransport_lane_for_profile
            raise _unsupported(f"webtransport lane {lane}")
    else:
        raise _unsupported(kind)

    event_key_inputs = {
        "family": family,
        "binding": kind,
        "framing": framing,
    }
    if kind == "webtransport":
        event_key_inputs["lane"] = lane
        event_key_inputs["inner_framing"] = inner_framing

    return {
        "op_id": op_id,
        "binding_kind": kind,
        "family": family,
        "framing": framing,
        "atom_anchors": anchors,
        "event_key_inputs": event_key_inputs,
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
