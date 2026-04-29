from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

DEFAULT_PHASES: tuple[str, ...] = (
    "INGRESS_PARSE",
    "PRE_HANDLER",
    "HANDLER",
    "POST_HANDLER",
    "POST_EMIT",
)


def compile_protocol_phase_tree(metadata: Mapping[str, Any]) -> dict[str, object]:
    binding = str(metadata.get("binding") or "unknown")
    subevent = str(metadata.get("subevent") or "unknown")
    phases = tuple(metadata.get("phases") or DEFAULT_PHASES)
    phases = tuple(phase for phase in phases if phase != "INGRESS_ROUTE")

    nodes: list[dict[str, object]] = []
    for index, phase in enumerate(phases):
        target = phases[index + 1] if index + 1 < len(phases) else "terminal"
        node_id = _node_id(binding, subevent, phase, index)
        nodes.append(
            {
                "node_id": node_id,
                "canonical_phase": phase,
                "ok_child": {"kind": "ok", "target": target},
                "err_child": {"kind": "err", "target": _err_target(binding, phase)},
            }
        )

    tree = {
        "binding": binding,
        "subevent": subevent,
        "nodes": tuple(nodes),
        "terminal_policy": _terminal_policy(binding),
    }
    validate_protocol_phase_tree(tree)
    return tree


def validate_protocol_phase_tree(tree: Mapping[str, Any]) -> None:
    nodes = tuple(tree.get("nodes") or ())
    seen: set[str] = set()
    for node in nodes:
        if not isinstance(node, Mapping):
            raise ValueError("phase tree node must be a mapping")
        node_id = node.get("node_id")
        if not node_id:
            raise ValueError("phase tree node_id is required")
        if str(node_id) in seen:
            raise ValueError(f"duplicate node_id in phase tree: {node_id}")
        seen.add(str(node_id))
        if not node.get("canonical_phase"):
            raise ValueError(f"phase tree node {node_id!r} missing canonical_phase")
        if node.get("terminal") is True and (
            node.get("ok_child") is not None or node.get("err_child") is not None
        ):
            raise ValueError("terminal phase tree node cannot have child edge metadata")
        ok_child = node.get("ok_child")
        err_child = node.get("err_child")
        if not isinstance(ok_child, Mapping) or ok_child.get("kind") != "ok":
            raise ValueError(f"phase tree node {node_id!r} missing ok edge")
        if not isinstance(err_child, Mapping) or err_child.get("kind") != "err":
            raise ValueError(
                f"phase tree node {node_id!r} missing err edge and ErrorCtx target"
            )


def linearize_protocol_phase_tree(tree: Mapping[str, Any]) -> tuple[str, ...]:
    phases: list[str] = []
    for node in tuple(tree.get("nodes") or ()):
        if isinstance(node, Mapping):
            phase = node.get("canonical_phase")
            if phase and phase not in phases and phase != "INGRESS_ROUTE":
                phases.append(str(phase))
    return tuple(phases)


def select_err_edge(
    node: Mapping[str, Any], exc: BaseException, metadata: Mapping[str, Any]
) -> dict[str, object]:
    err_child = node.get("err_child")
    if not isinstance(err_child, Mapping) or "target" not in err_child:
        raise ValueError("err edge is required to build ErrorCtx")

    error_ctx = {
        "node_id": node.get("node_id"),
        "failing_phase": node.get("canonical_phase"),
        "binding": metadata.get("binding"),
        "exchange": metadata.get("exchange"),
        "subevent": metadata.get("subevent"),
        "transaction_open": bool(metadata.get("transaction_open", False)),
        "rollback_required": bool(metadata.get("rollback_required", False)),
        "transport_started": bool(metadata.get("transport_started", False)),
        "emit_complete": bool(metadata.get("emit_complete", False)),
        "atom": node.get("atom"),
        "anchor": node.get("anchor"),
        "scope_type": node.get("scope_type"),
        "error_type": type(exc).__name__,
        "error": str(exc),
    }
    return {"kind": "err", "target": err_child["target"], "error_ctx": error_ctx}


def _node_id(binding: str, subevent: str, phase: str, index: int) -> str:
    raw = f"{binding}.{subevent}.{index}.{phase}".lower()
    return re.sub(r"[^a-z0-9_.]+", "_", raw)


def _terminal_policy(binding: str) -> str:
    if binding in {"http.stream", "http.sse"}:
        return "emit_complete"
    if binding.endswith(".datagram") or binding == "udp.datagram":
        return "ack"
    return "transport.close"


def _err_target(binding: str, phase: str) -> str:
    if phase in {"INGRESS_PARSE", "PRE_HANDLER"}:
        return "transport.close"
    if binding in {"http.stream", "http.sse"} and phase in {"EMIT", "POST_EMIT"}:
        return "POST_EMIT"
    if phase == "HANDLER":
        return "ON_HANDLER_ERROR"
    return "ON_ERROR"


__all__ = [
    "compile_protocol_phase_tree",
    "linearize_protocol_phase_tree",
    "select_err_edge",
    "validate_protocol_phase_tree",
]
