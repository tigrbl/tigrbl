from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tigrbl_core._spec.binding_spec import (
    derive_websocket_subprotocol_for_framing,
    framing_spec_name,
    normalize_framing_spec,
    validate_app_framing_for_binding,
    validate_binding_profile_exchange,
    validate_webtransport_inner_framing,
    validate_webtransport_lane_exchange,
    webtransport_lane_for_profile,
    webtransport_runtime_family,
)
from tigrbl_kernel.resume_policy import compile_resume_policy


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
    framing_kind = ""
    framing_spec = ""
    subprotocols: tuple[str, ...] = ()
    inner_framing: str | None = None
    rows: tuple[dict[str, str], ...]

    if kind in {"http.rest", "https.rest"}:
        validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "request_response"),
        )
        framing_spec_obj = normalize_framing_spec(framing, default="json")
        validate_app_framing_for_binding(binding_kind=kind, framing=framing_spec_obj)
        family = "request"
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
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
        rpc_method = binding.get("method") or binding.get("rpc_method")
        if not rpc_method:
            raise _unsupported("http.jsonrpc requires method")
        validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "request_response"),
        )
        framing_spec_obj = normalize_framing_spec(framing, default="jsonrpc")
        validate_app_framing_for_binding(binding_kind=kind, framing=framing_spec_obj)
        family = "request"
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
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
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "server_stream"),
        )
        framing_spec_obj = normalize_framing_spec(framing, default="stream")
        validate_app_framing_for_binding(binding_kind=kind, framing=framing_spec_obj)
        family = "stream"
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
        if exchange == "client_stream":
            anchors = (
                "transport.receive",
                "dispatch.subevent.derive",
                "handler.invoke",
                "transport.emit_complete",
            )
            rows = (
                {"family": "stream", "subevent": "stream.chunk.received"},
                {"family": "stream", "subevent": "stream.receive_complete"},
            )
        else:
            anchors = ("handler.invoke", "transport.emit", "transport.emit_complete")
            rows = (
                {"family": "stream", "subevent": "stream.chunk"},
                {"family": "stream", "subevent": "stream.close"},
            )
    elif kind in {"http.sse", "https.sse"}:
        validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "server_stream"),
        )
        framing_spec_obj = normalize_framing_spec(framing, default="sse")
        validate_app_framing_for_binding(binding_kind=kind, framing=framing_spec_obj)
        family = "stream"
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
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
        framing_spec_obj = normalize_framing_spec(framing, default="text")
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
        subprotocols = tuple(str(item).lower() for item in binding.get("subprotocols", ()))
        websocket_subprotocol = derive_websocket_subprotocol_for_framing(framing_spec_obj)
        validate_binding_profile_exchange(
            binding_kind="wss" if kind == "wss" else "ws",
            exchange=str(binding.get("exchange") or "bidirectional_stream"),
        )
        validate_app_framing_for_binding(
            binding_kind="wss" if kind == "wss" else "ws",
            framing=framing_spec_obj,
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
        framing_spec_obj = normalize_framing_spec(framing, default="webtransport")
        validate_app_framing_for_binding(binding_kind=kind, framing=framing_spec_obj)
        if framing and framing_spec_obj.kind != "webtransport":
            raise _unsupported("webtransport outer framing must remain webtransport")
        framing_kind = framing_spec_obj.kind
        framing_spec = framing_spec_obj.__class__.__name__
        control_stream = binding.get("control_stream")
        streams = tuple(binding.get("streams", ()) or ())
        datagrams = tuple(binding.get("datagrams", ()) or ())
        if control_stream is not None:
            control = dict(control_stream)
            if control.get("kind") != "bidi_stream":
                raise _unsupported("webtransport control_stream must use bidi_stream")
            if control.get("opens") != "first":
                raise _unsupported("webtransport control_stream must open first")
            control["framing"] = validate_webtransport_inner_framing(
                lane="bidi_stream",
                inner_framing=control.get("framing"),
            )
            stream_rows = []
            datagram_rows = []
            names: list[str] = []
            for stream in streams:
                row = dict(stream)
                name = str(row.get("name") or "")
                if not name:
                    raise _unsupported("webtransport streams require name")
                names.append(name)
                lane_kind = str(row.get("kind") or "")
                row["framing"] = validate_webtransport_inner_framing(
                    lane=lane_kind,
                    inner_framing=row.get("framing"),
                )
                stream_rows.append(row)
            for datagram in datagrams:
                row = dict(datagram)
                name = str(row.get("name") or "")
                if not name:
                    raise _unsupported("webtransport datagrams require name")
                names.append(name)
                row["framing"] = validate_webtransport_inner_framing(
                    lane="datagram",
                    inner_framing=row.get("framing"),
                )
                datagram_rows.append(row)
            if len(set(names)) != len(names):
                raise _unsupported("webtransport lane names must be unique")
            family = "session"
            lane = "session"
            inner_framing = None
            framing = framing_spec_obj.kind
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
            lane_catalog = {
                "control_stream": control,
                "streams": tuple(stream_rows),
                "datagrams": tuple(datagram_rows),
            }
        else:
            lane_catalog = None
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
            framing = framing_spec_obj.kind
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
    if subprotocols:
        event_key_inputs["subprotocols"] = subprotocols
    if kind in {"ws", "wss", "websocket"} and websocket_subprotocol is not None:
        event_key_inputs["websocket_subprotocol"] = websocket_subprotocol
    if kind == "webtransport":
        event_key_inputs["lane"] = lane
        event_key_inputs["inner_framing"] = inner_framing
        if lane_catalog is not None:
            event_key_inputs["lane_catalog"] = lane_catalog
    resume_policy = compile_resume_policy(kind, binding)
    if resume_policy.enabled:
        event_key_inputs["resume_mode"] = resume_policy.mode

    plan: dict[str, object] = {
        "op_id": op_id,
        "binding_kind": kind,
        "family": family,
        "framing": framing,
        "framing_kind": framing_kind or str(framing),
        "framing_spec": framing_spec or framing_spec_name(str(framing)),
        "atom_anchors": anchors,
        "event_key_inputs": event_key_inputs,
        "capability_requirements": {
            "required_mask": _required_mask(kind=kind, family=family, framing=str(framing)),
        },
        "lifecycle_rows": rows,
    }
    if subprotocols:
        plan["subprotocols"] = subprotocols
    if kind in {"ws", "wss", "websocket"} and websocket_subprotocol is not None:
        plan["websocket_subprotocol"] = websocket_subprotocol
    if kind == "webtransport":
        plan["inner_framing"] = inner_framing
        if lane_catalog is not None:
            plan["lane_catalog"] = lane_catalog
    if resume_policy.enabled:
        plan["resume_policy"] = resume_policy.as_dict()
    return plan


def _required_mask(*, kind: str, family: str, framing: str) -> int:
    source = f"{kind}:{family}:{framing}".encode("utf-8")
    value = 0
    for byte in source:
        value = ((value << 5) ^ byte) & 0xFFFF_FFFF
    return value


__all__ = ["compile_binding_protocol_plan"]
