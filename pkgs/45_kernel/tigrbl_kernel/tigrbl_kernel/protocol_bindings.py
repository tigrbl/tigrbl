from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tigrbl_core._spec.binding_spec import (
    BytesFramingSpec,
    derive_websocket_subprotocol_for_framing,
    framing_spec_name,
    framing_kind as framing_spec_kind,
    framing_spec_from_kind,
    JsonFramingSpec,
    JsonRpcFramingSpec,
    normalize_framing_spec,
    SseFramingSpec,
    TextFramingSpec,
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


def _binding_get(binding: Any, key: str, default: Any = None) -> Any:
    if isinstance(binding, Mapping):
        return binding.get(key, default)
    return getattr(binding, key, default)


def _lane_mapping(value: Any, *, lane_kind: str | None = None) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    row: dict[str, Any] = {}
    for key in ("name", "kind", "opens", "purpose", "framing"):
        item = getattr(value, key, None)
        if item is not None:
            row[key] = item
    if lane_kind is not None:
        row.setdefault("kind", lane_kind)
    return row


def compile_binding_protocol_plan(op_id: str, binding: Any) -> dict[str, object]:
    kind = _binding_get(binding, "kind") or _binding_get(binding, "proto")
    if not kind:
        raise ValueError(
            "BindingSpec binding source is required; transport guessing is ambiguous"
        )

    kind = str(kind)
    profile = _binding_get(binding, "profile")
    if kind in {"http", "https"} and profile:
        kind = f"{kind}.{profile}"
    elif kind == "websocket":
        kind = str(_binding_get(binding, "proto") or "ws")
    framing = _binding_get(binding, "framing")
    framing_kind = ""
    framing_spec = ""
    subprotocols: tuple[str, ...] = ()
    inner_framing: str | None = None
    rows: tuple[dict[str, str], ...]
    rpc_path: str | None = None
    rpc_method: str | None = None

    if kind in {"http.rest", "https.rest"}:
        validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(_binding_get(binding, "exchange") or "request_response"),
        )
        framing_spec_obj = normalize_framing_spec(
            framing_spec_from_kind(framing),
            default=JsonFramingSpec(),
        )
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
        rpc_method = _binding_get(binding, "method") or _binding_get(binding, "rpc_method")
        if not rpc_method:
            raise _unsupported("http.jsonrpc requires method")
        rpc_method = str(rpc_method)
        rpc_path = str(
            _binding_get(binding, "path", _binding_get(binding, "endpoint", "/rpc"))
            or "/rpc"
        )
        validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(_binding_get(binding, "exchange") or "request_response"),
        )
        framing_spec_obj = normalize_framing_spec(
            framing_spec_from_kind(framing),
            default=JsonRpcFramingSpec(),
        )
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
            exchange=str(_binding_get(binding, "exchange") or "server_stream"),
        )
        framing_spec_obj = normalize_framing_spec(
            framing_spec_from_kind(framing),
            default=BytesFramingSpec(),
        )
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
            exchange=str(_binding_get(binding, "exchange") or "server_stream"),
        )
        framing_spec_obj = normalize_framing_spec(
            framing_spec_from_kind(framing),
            default=SseFramingSpec(),
        )
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
        if _binding_get(binding, "methods"):
            raise _unsupported("websocket bindings do not accept HTTP methods")
        family = "message"
        framing_spec_obj = normalize_framing_spec(
            framing_spec_from_kind(framing),
            default=TextFramingSpec(),
        )
        framing = framing_spec_obj.kind
        framing_kind = framing
        framing_spec = framing_spec_obj.__class__.__name__
        subprotocols = tuple(str(item).lower() for item in (_binding_get(binding, "subprotocols", ()) or ()))
        websocket_subprotocol = derive_websocket_subprotocol_for_framing(framing_spec_obj)
        validate_binding_profile_exchange(
            binding_kind="wss" if kind == "wss" else "ws",
            exchange=str(_binding_get(binding, "exchange") or "bidirectional_stream"),
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
        if _binding_get(binding, "exchange") == "request_response":
            raise _unsupported("webtransport request_response exchange")
        if framing is not None:
            raise _unsupported("webtransport bindings do not accept top-level app framing")
        framing_kind = ""
        framing_spec = ""
        control_stream = _binding_get(binding, "control_stream")
        streams = tuple(_binding_get(binding, "streams", ()) or ())
        datagrams = tuple(_binding_get(binding, "datagrams", ()) or ())
        if control_stream is not None or streams or datagrams:
            control = None
            if control_stream is not None:
                control = _lane_mapping(control_stream, lane_kind="bidi_stream")
                if control.get("kind") != "bidi_stream":
                    raise _unsupported("webtransport control_stream must use bidi_stream")
                if control.get("opens") != "first":
                    raise _unsupported("webtransport control_stream must open first")
                control_framing = validate_webtransport_inner_framing(
                    lane="bidi_stream",
                    inner_framing=framing_spec_from_kind(control.get("framing")),
                )
                control["framing"] = framing_spec_kind(control_framing)
                control["framing_spec"] = framing_spec_name(control_framing)
            stream_rows = []
            datagram_rows = []
            names: list[str] = []
            for stream in streams:
                row = _lane_mapping(stream)
                name = str(row.get("name") or "")
                if not name:
                    raise _unsupported("webtransport streams require name")
                names.append(name)
                lane_kind = str(row.get("kind") or "")
                stream_framing = validate_webtransport_inner_framing(
                    lane=lane_kind,
                    inner_framing=framing_spec_from_kind(row.get("framing")),
                )
                row["framing"] = framing_spec_kind(stream_framing)
                row["framing_spec"] = framing_spec_name(stream_framing)
                stream_rows.append(row)
            for datagram in datagrams:
                row = _lane_mapping(datagram)
                name = str(row.get("name") or "")
                if not name:
                    raise _unsupported("webtransport datagrams require name")
                names.append(name)
                datagram_framing = validate_webtransport_inner_framing(
                    lane="datagram",
                    inner_framing=framing_spec_from_kind(row.get("framing")),
                )
                row["framing"] = framing_spec_kind(datagram_framing)
                row["framing_spec"] = framing_spec_name(datagram_framing)
                datagram_rows.append(row)
            if len(set(names)) != len(names):
                raise _unsupported("webtransport lane names must be unique")
            family = "session"
            lane = "session"
            inner_framing = None
            framing = ""
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
                _binding_get(binding, "lane") or _binding_get(binding, "profile") or "webtransport"
            )
            validate_webtransport_lane_exchange(
                lane=lane,
                exchange=str(_binding_get(binding, "exchange") or {
                    "session": "bidirectional_stream",
                    "bidi_stream": "bidirectional_stream",
                    "unidi_client_stream": "client_stream",
                    "unidi_server_stream": "server_stream",
                    "datagram": "bidirectional_stream",
                }[lane]),
            )
            inner_framing = validate_webtransport_inner_framing(
                lane=lane,
                inner_framing=framing_spec_from_kind(_binding_get(binding, "inner_framing")),
            )
            family = webtransport_runtime_family(lane)
            framing = framing_spec_kind(inner_framing)
            framing_kind = framing
            framing_spec = framing_spec_name(inner_framing)
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
    if kind in {"http.jsonrpc", "https.jsonrpc"}:
        event_key_inputs["path"] = rpc_path
        event_key_inputs["method"] = rpc_method
    if kind in {"ws", "wss", "websocket"} and websocket_subprotocol is not None:
        event_key_inputs["websocket_subprotocol"] = websocket_subprotocol
    if kind == "webtransport":
        event_key_inputs["lane"] = lane
        if lane_catalog is not None:
            event_key_inputs["lane_catalog"] = lane_catalog
        else:
            event_key_inputs["inner_framing"] = framing_spec_kind(inner_framing)
            event_key_inputs["inner_framing_spec"] = framing_spec_name(inner_framing)
    resume_policy = compile_resume_policy(kind, binding if isinstance(binding, Mapping) else {})
    if resume_policy.enabled:
        event_key_inputs["resume_mode"] = resume_policy.mode

    plan: dict[str, object] = {
        "op_id": op_id,
        "binding_kind": kind,
        "family": family,
        "framing": framing,
        "framing_kind": framing_kind or str(framing),
        "framing_spec": framing_spec,
        "atom_anchors": anchors,
        "event_key_inputs": event_key_inputs,
        "capability_requirements": {
            "required_mask": _required_mask(kind=kind, family=family, framing=str(framing)),
        },
        "lifecycle_rows": rows,
    }
    if subprotocols:
        plan["subprotocols"] = subprotocols
    if kind in {"http.jsonrpc", "https.jsonrpc"}:
        plan["path"] = rpc_path
        plan["method"] = rpc_method
    if kind in {"ws", "wss", "websocket"} and websocket_subprotocol is not None:
        plan["websocket_subprotocol"] = websocket_subprotocol
    if kind == "webtransport":
        if lane_catalog is not None:
            plan["lane_catalog"] = lane_catalog
        else:
            plan["inner_framing"] = framing_spec_kind(inner_framing)
            plan["inner_framing_kind"] = framing_spec_kind(inner_framing)
            plan["inner_framing_spec"] = framing_spec_name(inner_framing)
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
