from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

ANCHORS: tuple[str, ...] = (
    "transport.accept",
    "transport.receive",
    "framing.decode",
    "CALL_HANDLER",
    "framing.encode",
    "transport.emit",
    "transport.close",
)

SESSION_LIFECYCLE_PHASES: tuple[str, ...] = (
    "SESSION_OPEN",
    "POST_SESSION_OPEN",
    "MESSAGE_RECEIVE",
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
    "EGRESS_SHAPE",
    "EGRESS_FINALIZE",
    "POST_RESPONSE",
    "PRE_SESSION_CLOSE",
    "SESSION_CLOSE",
    "POST_SESSION_CLOSE",
)

SESSION_STRUCTURAL_PHASES: tuple[str, ...] = (
    "SESSION_OPEN",
    "MESSAGE_RECEIVE",
    "SESSION_CLOSE",
)

SESSION_HOOK_PHASES: tuple[str, ...] = (
    "POST_SESSION_OPEN",
    "PRE_SESSION_CLOSE",
    "POST_SESSION_CLOSE",
)

CORE_REALTIME_ATOMS: tuple[str, ...] = (
    "transport.accept",
    "transport.receive",
    "transport.emit",
    "transport.close",
    "framing.decode",
    "framing.encode",
    "dispatch.binding.match",
    "dispatch.binding.parse",
    "subscription.register",
    "subscription.unregister",
    "publish.prepare",
    "publish.enqueue",
    "publish.fanout",
)

ATOM_PHASE_PLACEMENT: dict[str, str] = {
    "transport.accept": "SESSION_OPEN",
    "transport.receive": "MESSAGE_RECEIVE",
    "dispatch.binding.match": "INGRESS_DISPATCH",
    "dispatch.binding.parse": "INGRESS_DISPATCH",
    "framing.decode": "INGRESS_PARSE",
    "subscription.register": "POST_COMMIT",
    "subscription.unregister": "PRE_SESSION_CLOSE",
    "publish.prepare": "POST_COMMIT",
    "publish.enqueue": "POST_COMMIT",
    "publish.fanout": "EGRESS_FINALIZE",
    "framing.encode": "EGRESS_FINALIZE",
    "transport.emit": "EGRESS_FINALIZE",
    "transport.close": "SESSION_CLOSE",
}

PUBLISH_POLICY: dict[str, object] = {
    "automatic_for_oltp": False,
    "publish_only_op": True,
    "create_only_publishes": False,
    "create_and_publish_requires_effect": True,
    "rollback_suppresses_publish": True,
    "placement": {
        "HANDLER": ("publish.intent",),
        "POST_COMMIT": ("publish.prepare", "publish.enqueue"),
        "EGRESS_FINALIZE": ("publish.fanout", "framing.encode", "transport.emit"),
        "POST_RESPONSE": ("cleanup.metrics",),
    },
}

SUBSCRIBE_POLICY: dict[str, object] = {
    "operation_shape": "finite_request_response",
    "ack_framing": "jsonrpc",
    "owns_receive_loop": False,
    "registration": {"atom": "subscription.register", "phase": "POST_COMMIT"},
    "cleanup": {"atom": "subscription.unregister", "phase": "PRE_SESSION_CLOSE"},
}


def _binding_framing(binding: Mapping[str, Any]) -> str:
    framing = (
        binding.get("framing", "text")
        if isinstance(binding, Mapping)
        else getattr(binding, "framing", "text")
    )
    if isinstance(framing, str):
        return framing.lower()
    name = type(framing).__name__.lower()
    if "jsonrpc" in name:
        return "jsonrpc"
    if "ndjson" in name:
        return "ndjson"
    if "text" in name:
        return "text"
    return name


def _binding_path(binding: Mapping[str, Any]) -> str | None:
    if isinstance(binding, Mapping):
        path = binding.get("path") or binding.get("connect_path")
    else:
        path = getattr(binding, "path", None) or getattr(
            binding,
            "connect_path",
            None,
        )
    return str(path) if path is not None else None


def _op_bindings(op: Any) -> tuple[Any, ...]:
    bindings = (
        op.get("bindings", ())
        if isinstance(op, Mapping)
        else getattr(op, "bindings", ())
    )
    return tuple(bindings or ())


def _op_alias(op: Any) -> str:
    alias = op.get("alias") if isinstance(op, Mapping) else getattr(op, "alias", None)
    if not isinstance(alias, str) or not alias:
        raise ValueError("websocket jsonrpc op requires alias")
    return alias


def _op_method(op: Any) -> str:
    if isinstance(op, Mapping):
        method = (
            op.get("op_method")
            or op.get("op_id")
            or op.get("identity")
            or op.get("canonical_identity")
            or op.get("name")
        )
    else:
        method = (
            getattr(op, "op_method", None)
            or getattr(op, "op_id", None)
            or getattr(op, "identity", None)
            or getattr(op, "canonical_identity", None)
            or getattr(op, "name", None)
        )
        if method is None:
            table = getattr(op, "table", None)
            table_name = getattr(table, "__name__", None)
            alias = getattr(op, "alias", None)
            if table_name and alias:
                method = f"{table_name}.{alias}"
            elif alias:
                method = str(alias)
    if not isinstance(method, str) or not method:
        raise ValueError("websocket jsonrpc op requires canonical op identity")
    return method


def _table_identity(table: Any) -> str:
    name = getattr(table, "name", None)
    if isinstance(name, str) and name:
        return name
    model = getattr(table, "model", None)
    model_name = getattr(model, "__name__", None)
    if isinstance(model_name, str) and model_name:
        return model_name
    model_ref = getattr(table, "model_ref", None)
    if isinstance(model_ref, str) and model_ref:
        return model_ref.rsplit(":", 1)[-1].rsplit(".", 1)[-1]
    resource = getattr(table, "resource", None)
    if isinstance(resource, str) and resource:
        return resource
    raise ValueError("websocket jsonrpc table requires name, model, or model_ref")


def _binding_proto(binding: Any) -> str:
    if isinstance(binding, Mapping):
        proto = binding.get("proto") or binding.get("protocol") or "ws"
    else:
        proto = getattr(binding, "proto", None) or getattr(binding, "protocol", None)
    return str(proto or "ws").lower()


def _register_jsonrpc_op(
    endpoint: dict[str, Any],
    *,
    path: str,
    method: str,
    op: Any,
) -> None:
    for binding in _op_bindings(op):
        if _binding_path(binding) != path:
            continue
        if _binding_proto(binding) not in {"ws", "wss", "websocket"}:
            continue
        if _binding_framing(binding) != "jsonrpc":
            continue
        if method in endpoint:
            raise ValueError(
                f"duplicate websocket jsonrpc registration for {path} {method}"
            )
        endpoint[method] = op


def compile_websocket_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    scheme = binding.get("scheme", "ws")
    if scheme not in {"ws", "wss"}:
        raise ValueError("websocket scheme must be ws or wss")
    framing = _binding_framing(binding)
    tls = dict((binding.get("extensions") or {}).get("tls") or {})
    return {
        "binding": "wss" if scheme == "wss" else "websocket",
        "exchange": "bidirectional_stream",
        "family": "message",
        "path": binding.get("path"),
        "framing": framing,
        "anchors": ANCHORS,
        "lifecycle_phases": SESSION_LIFECYCLE_PHASES,
        "structural_phases": SESSION_STRUCTURAL_PHASES,
        "hook_phases": SESSION_HOOK_PHASES,
        "realtime_atoms": CORE_REALTIME_ATOMS,
        "atom_phase_placement": ATOM_PHASE_PLACEMENT,
        "subscribe_policy": SUBSCRIBE_POLICY,
        "publish_policy": PUBLISH_POLICY,
        "loop_region": {
            "loop_id": "websocket.receive",
            "role": "message",
            "break_conditions": ("websocket.disconnect",),
            "enter_phase": "MESSAGE_RECEIVE",
            "exit_target": "PRE_SESSION_CLOSE",
        },
        "close": {"code": 1000, "reason": ""},
        "scope_metadata": {
            "secure": scheme == "wss",
            "tls": tls,
        },
    }


def compile_websocket_jsonrpc_dispatch_index(
    *,
    path: str,
    ops: Iterable[Any] = (),
    tables: Iterable[Any] = (),
) -> dict[str, object]:
    endpoint: dict[str, Any] = {}
    for table in tables:
        table_name = _table_identity(table)
        for op in tuple(getattr(table, "ops", ()) or ()):
            _register_jsonrpc_op(
                endpoint,
                path=path,
                method=f"{table_name}.{_op_alias(op)}",
                op=op,
            )
    for op in ops:
        _register_jsonrpc_op(
            endpoint,
            path=path,
            method=_op_method(op),
            op=op,
        )
    return {
        "ws": {"exact": {path: "session_program"}},
        "ws.jsonrpc": {"endpoints": {path: endpoint}},
    }


__all__ = [
    "ATOM_PHASE_PLACEMENT",
    "CORE_REALTIME_ATOMS",
    "PUBLISH_POLICY",
    "SESSION_HOOK_PHASES",
    "SESSION_LIFECYCLE_PHASES",
    "SESSION_STRUCTURAL_PHASES",
    "SUBSCRIBE_POLICY",
    "compile_websocket_chain",
    "compile_websocket_jsonrpc_dispatch_index",
]
