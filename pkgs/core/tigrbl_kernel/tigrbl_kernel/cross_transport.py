from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any

from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


TRANSPORT_ENVELOPE_KEYS = frozenset(
    {
        "headers",
        "http_status",
        "jsonrpc_id",
        "jsonrpc_version",
        "path",
        "rpc_method",
        "stream_id",
        "transport",
        "ws_opcode",
    }
)


@dataclass(frozen=True)
class EquivalenceCase:
    op_id: str
    category: str
    bindings: tuple[Mapping[str, Any], ...]


def canonical_operation_id(op_id: str) -> str:
    normalized = str(op_id).strip()
    if not normalized or "." not in normalized:
        raise ValueError("canonical operation id must be a non-empty table.operation token")
    table, op = normalized.split(".", maxsplit=1)
    if not table or not op:
        raise ValueError("canonical operation id requires table and operation components")
    return f"{table}.{op}"


def compile_equivalence_manifest(
    op_id: str,
    bindings: Iterable[Mapping[str, Any]],
    *,
    schema_identity: str = "schema:v1",
    runtime_plan_identity: str = "runtime-plan:v1",
) -> dict[str, Any]:
    canonical_id = canonical_operation_id(op_id)
    plans = tuple(compile_binding_protocol_plan(canonical_id, binding) for binding in bindings)
    if not plans:
        raise ValueError("at least one transport binding is required")
    return {
        "op_id": canonical_id,
        "schema_identity": str(schema_identity),
        "runtime_plan_identity": str(runtime_plan_identity),
        "bindings": tuple(_plan_fingerprint(plan) for plan in plans),
    }


def normalized_transport_result(result: Mapping[str, Any]) -> dict[str, Any]:
    semantic = {
        key: _freeze(value)
        for key, value in result.items()
        if key not in TRANSPORT_ENVELOPE_KEYS
    }
    if "diagnostics" in semantic and isinstance(semantic["diagnostics"], Mapping):
        diagnostics = dict(semantic["diagnostics"])
        diagnostics.pop("trace_id", None)
        diagnostics.pop("qlog_id", None)
        semantic["diagnostics"] = _freeze(diagnostics)
    return dict(sorted(semantic.items()))


def equivalent_transport_results(*results: Mapping[str, Any]) -> bool:
    if not results:
        raise ValueError("at least one transport result is required")
    first = normalized_transport_result(results[0])
    return all(normalized_transport_result(result) == first for result in results[1:])


def equivalent_binding_group(op_id: str, bindings: Iterable[Mapping[str, Any]]) -> bool:
    manifest = compile_equivalence_manifest(op_id, bindings)
    families = {binding["family"] for binding in manifest["bindings"]}
    return bool(families) and len({manifest["op_id"]}) == 1


def standard_equivalence_corpus() -> tuple[EquivalenceCase, ...]:
    return (
        EquivalenceCase(
            "Item.read",
            "standard",
            (
                {"kind": "http.rest", "path": "/items/{id}", "methods": ("GET",)},
                {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
                {"kind": "ws", "path": "/socket", "framing": "jsonrpc", "subprotocols": ("jsonrpc",)},
            ),
        ),
        EquivalenceCase(
            "Item.bulk_create",
            "bulk",
            (
                {"kind": "http.rest", "path": "/items/bulk", "methods": ("POST",)},
                {"kind": "http.jsonrpc", "rpc_method": "Item.bulk_create"},
            ),
        ),
        EquivalenceCase(
            "Item.search",
            "query",
            (
                {"kind": "http.rest", "path": "/items", "methods": ("GET",)},
                {"kind": "http.jsonrpc", "rpc_method": "Item.search"},
            ),
        ),
        EquivalenceCase(
            "Item.tail",
            "stream",
            (
                {"kind": "http.stream", "path": "/items/tail"},
                {"kind": "http.sse", "path": "/items/events"},
                {"kind": "webtransport", "profile": "bidi_stream"},
            ),
        ),
        EquivalenceCase(
            "Item.custom_action",
            "custom",
            (
                {"kind": "http.jsonrpc", "rpc_method": "Item.custom_action"},
            ),
        ),
    )


def _plan_fingerprint(plan: Mapping[str, Any]) -> dict[str, Any]:
    stable = {
        "binding_kind": plan["binding_kind"],
        "family": plan["family"],
        "framing": plan["framing"],
        "capability_mask": plan["capability_requirements"]["required_mask"],
        "lifecycle": tuple(
            (row["family"], row["subevent"]) for row in plan["lifecycle_rows"]
        ),
    }
    stable["fingerprint"] = sha256(repr(stable).encode("utf-8")).hexdigest()
    return stable


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _freeze(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


__all__ = [
    "EquivalenceCase",
    "canonical_operation_id",
    "compile_equivalence_manifest",
    "equivalent_binding_group",
    "equivalent_transport_results",
    "normalized_transport_result",
    "standard_equivalence_corpus",
]
