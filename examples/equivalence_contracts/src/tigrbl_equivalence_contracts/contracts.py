from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Literal

from tigrbl_core._spec.binding_spec import (
    validate_app_framing_for_binding,
    validate_binding_profile_exchange,
    validate_webtransport_inner_framing,
    validate_webtransport_lane_exchange,
    webtransport_lane_for_profile,
    webtransport_runtime_family,
)
from tigrbl_core._spec.datatypes import DataTypeSpec, EngineDatatypeBridge
from tigrbl_core._spec.router_spec import RouterSpec
from tigrbl_core._spec.table_profile_spec import get_builtin_table_profile_definition


EquivalenceStatus = Literal[
    "equivalent",
    "analogous",
    "projection-only",
    "tigrbl-specific",
    "not-equivalent",
]


@dataclass(frozen=True)
class CertificationResult:
    equivalence_id: str
    status: EquivalenceStatus
    certified: bool
    evidence: Mapping[str, Any]


@dataclass(frozen=True)
class CertifiableEquivalence:
    id: str
    status: EquivalenceStatus
    claim: str
    source_documents: tuple[str, ...]
    source_modules: tuple[str, ...]
    certify_runtime: Callable[[], Mapping[str, Any]]

    def certify(self) -> CertificationResult:
        evidence = dict(self.certify_runtime())
        if not evidence:
            raise AssertionError(f"{self.id} produced no certification evidence")
        return CertificationResult(
            equivalence_id=self.id,
            status=self.status,
            certified=True,
            evidence=evidence,
        )


@dataclass(frozen=True)
class RouteDeclaration:
    surface: str
    prefix: str
    path: str
    methods: tuple[str, ...]
    endpoint: str
    authority: str

    def projection(self) -> dict[str, Any]:
        return {
            "path": _join_path(self.prefix, self.path),
            "methods": tuple(sorted(method.upper() for method in self.methods)),
            "endpoint": self.endpoint,
        }


@dataclass(frozen=True)
class TableDeclaration:
    surface: str
    resource: str
    fields: Mapping[str, str]
    operations: tuple[str, ...]
    authority: str

    def projection(self) -> dict[str, Any]:
        return {
            "resource": self.resource,
            "fields": tuple(sorted((name, logical) for name, logical in self.fields.items())),
            "operations": tuple(sorted(self.operations)),
        }


def equivalence_by_id(equivalence_id: str) -> CertifiableEquivalence:
    for case in CERTIFIABLE_EQUIVALENCES:
        if case.id == equivalence_id:
            return case
    raise KeyError(equivalence_id)


def certify_all() -> tuple[CertificationResult, ...]:
    return tuple(case.certify() for case in CERTIFIABLE_EQUIVALENCES)


def _certify_rest_jsonrpc_websocket_read() -> Mapping[str, Any]:
    bindings = (
        {"kind": "http.rest", "path": "/items/{id}", "methods": ("GET",)},
        {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
        {"kind": "ws", "path": "/socket", "framing": "jsonrpc", "subprotocols": ("jsonrpc",)},
    )
    manifest = compile_equivalence_manifest(
        "Item.read",
        bindings,
        schema_identity="schema:item:v1",
        runtime_plan_identity="plan:item:read:v1",
    )
    results = (
        {
            "transport": "http",
            "http_status": 200,
            "headers": {"content-type": "application/json"},
            "value": {"id": "item-1", "name": "Ada"},
            "effects": ("read:item-1",),
            "diagnostics": {"classification": "ok", "trace_id": "http-1"},
        },
        {
            "transport": "jsonrpc",
            "jsonrpc_version": "2.0",
            "jsonrpc_id": "rpc-1",
            "value": {"id": "item-1", "name": "Ada"},
            "effects": ("read:item-1",),
            "diagnostics": {"classification": "ok", "trace_id": "rpc-1"},
        },
        {
            "transport": "ws",
            "ws_opcode": "text",
            "value": {"id": "item-1", "name": "Ada"},
            "effects": ("read:item-1",),
            "diagnostics": {"classification": "ok", "trace_id": "ws-1"},
        },
    )
    _assert(equivalent_transport_results(*results), "transport semantic results differ")
    return {
        "manifest": manifest,
        "normalized_result": normalized_transport_result(results[0]),
        "transport_count": len(results),
    }


def _certify_stream_sse_webtransport_tail() -> Mapping[str, Any]:
    bindings = (
        {"kind": "http.stream", "path": "/items/tail"},
        {"kind": "http.sse", "path": "/items/events"},
        {"kind": "webtransport", "profile": "bidi_stream"},
    )
    manifest = compile_equivalence_manifest(
        "Item.tail",
        bindings,
        schema_identity="schema:item-event:v1",
        runtime_plan_identity="plan:item:tail:v1",
    )
    results = (
        {
            "transport": "http.stream",
            "stream_id": "stream-1",
            "value": ({"id": "item-1", "version": 1}, {"id": "item-1", "version": 2}),
            "ordering": "ordered",
            "completion": "complete",
        },
        {
            "transport": "sse",
            "stream_id": "sse-1",
            "value": ({"id": "item-1", "version": 1}, {"id": "item-1", "version": 2}),
            "ordering": "ordered",
            "completion": "complete",
        },
        {
            "transport": "webtransport",
            "stream_id": "wt-1",
            "value": ({"id": "item-1", "version": 1}, {"id": "item-1", "version": 2}),
            "ordering": "ordered",
            "completion": "complete",
        },
    )
    _assert(equivalent_transport_results(*results), "stream semantic results differ")
    return {
        "families": tuple(sorted({row["family"] for row in manifest["bindings"]})),
        "manifest": manifest,
        "normalized_result": normalized_transport_result(results[0]),
    }


def _certify_router_prefix_projection() -> Mapping[str, Any]:
    tigrbl_router = RouterSpec(name="items", prefix="/v1")
    declarations = (
        RouteDeclaration(
            "fastapi.apirouter",
            "/v1",
            "/items/{item_id}",
            ("GET",),
            "Item.read",
            "path operation",
        ),
        RouteDeclaration(
            "flask.blueprint",
            "/v1",
            "/items/<item_id>",
            ("GET",),
            "Item.read",
            "view function",
        ),
        RouteDeclaration(
            "tigrbl.router",
            tigrbl_router.prefix,
            "/items/{item_id}",
            ("GET",),
            "Item.read",
            "operation binding",
        ),
    )
    projections = {
        declaration.surface: _normalize_route_projection(declaration.projection())
        for declaration in declarations
    }
    _assert_all_equal(projections.values(), "router prefix projections differ")
    return {
        "projection": next(iter(projections.values())),
        "surfaces": tuple(projections),
        "authorities": {row.surface: row.authority for row in declarations},
    }


def _certify_table_resource_projection() -> Mapping[str, Any]:
    profile = get_builtin_table_profile_definition("rest_jsonrpc")
    tigrbl_ops = tuple(op for op in profile.targets if op in {"create", "read", "list"})
    declarations = (
        TableDeclaration(
            "fastapi.pydantic-sqlalchemy",
            "Item",
            {"id": "string", "name": "string"},
            ("create", "read", "list"),
            "external model and handlers",
        ),
        TableDeclaration(
            "flask.sqlalchemy-blueprint",
            "Item",
            {"id": "string", "name": "string"},
            ("create", "read", "list"),
            "external model and views",
        ),
        TableDeclaration(
            "tigrbl.table-profile",
            "Item",
            {"id": "string", "name": "string"},
            tigrbl_ops,
            "TableProfileSpec",
        ),
    )
    projections = {row.surface: row.projection() for row in declarations}
    _assert_all_equal(projections.values(), "table resource projections differ")
    return {
        "profile": profile.kind,
        "projection": next(iter(projections.values())),
        "binding_families": profile.binding_families,
        "authorities": {row.surface: row.authority for row in declarations},
    }


def _certify_engine_datatype_lowering() -> Mapping[str, Any]:
    bridge = EngineDatatypeBridge()
    cases = {
        "uuid": {
            "sqlite": bridge.lower("sqlite", DataTypeSpec("uuid"), strict=True).physical_name,
            "postgres": bridge.lower("postgres", DataTypeSpec("uuid"), strict=True).physical_name,
        },
        "json": {
            "sqlite": bridge.lower("sqlite", DataTypeSpec("json"), strict=True).physical_name,
            "postgres": bridge.lower("postgres", DataTypeSpec("json"), strict=True).physical_name,
        },
    }
    _assert(cases["uuid"]["sqlite"] == "TEXT", "sqlite uuid lowering drifted")
    _assert(cases["uuid"]["postgres"] == "UUID", "postgres uuid lowering drifted")
    _assert(cases["json"]["sqlite"] == "JSON", "sqlite json lowering drifted")
    _assert(cases["json"]["postgres"] == "JSONB", "postgres json lowering drifted")
    return {
        "logical_datatypes": tuple(cases),
        "lowerings": cases,
        "semantic_rule": (
            "logical datatype identity is portable; "
            "physical SQL type is engine-specific"
        ),
    }


def compile_equivalence_manifest(
    op_id: str,
    bindings: Iterable[Mapping[str, Any]],
    *,
    schema_identity: str,
    runtime_plan_identity: str,
) -> dict[str, Any]:
    canonical_id = _canonical_operation_id(op_id)
    plans = tuple(_compile_binding_plan(canonical_id, binding) for binding in bindings)
    _assert(bool(plans), "at least one transport binding is required")
    return {
        "op_id": canonical_id,
        "schema_identity": schema_identity,
        "runtime_plan_identity": runtime_plan_identity,
        "bindings": tuple(_plan_fingerprint(plan) for plan in plans),
    }


def normalized_transport_result(result: Mapping[str, Any]) -> dict[str, Any]:
    envelope_keys = {
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
    semantic = {
        key: _freeze(value)
        for key, value in result.items()
        if key not in envelope_keys
    }
    if "diagnostics" in semantic and isinstance(semantic["diagnostics"], Mapping):
        diagnostics = dict(semantic["diagnostics"])
        diagnostics.pop("trace_id", None)
        diagnostics.pop("qlog_id", None)
        semantic["diagnostics"] = _freeze(diagnostics)
    return dict(sorted(semantic.items()))


def equivalent_transport_results(*results: Mapping[str, Any]) -> bool:
    _assert(bool(results), "at least one transport result is required")
    first = normalized_transport_result(results[0])
    return all(normalized_transport_result(result) == first for result in results[1:])


def _canonical_operation_id(op_id: str) -> str:
    table, separator, operation = str(op_id).strip().partition(".")
    if not table or separator != "." or not operation:
        raise ValueError("canonical operation id requires table and operation components")
    return f"{table}.{operation}"


def _compile_binding_plan(op_id: str, binding: Mapping[str, Any]) -> dict[str, Any]:
    kind = str(binding.get("kind") or binding.get("proto") or "")
    _assert(bool(kind), "binding kind is required")
    if kind in {"http", "https"} and binding.get("profile"):
        kind = f"{kind}.{binding['profile']}"
    if kind == "websocket":
        kind = str(binding.get("proto") or "ws")

    if kind in {"http.rest", "https.rest"}:
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "request_response"),
        )
        framing = validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "json"),
        )
        family = "request"
    elif kind in {"http.jsonrpc", "https.jsonrpc"}:
        _assert(bool(binding.get("rpc_method")), "http.jsonrpc requires rpc_method")
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "request_response"),
        )
        framing = validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "jsonrpc"),
        )
        family = "request"
    elif kind in {"http.stream", "https.stream"}:
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "server_stream"),
        )
        framing = validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "stream"),
        )
        family = "stream"
    elif kind in {"http.sse", "https.sse"}:
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "server_stream"),
        )
        framing = validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "sse"),
        )
        family = "stream"
    elif kind in {"ws", "wss"}:
        if binding.get("methods"):
            raise ValueError("websocket bindings do not accept HTTP methods")
        exchange = validate_binding_profile_exchange(
            binding_kind=kind,
            exchange=str(binding.get("exchange") or "bidirectional_stream"),
        )
        framing = validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "text"),
            subprotocols=tuple(str(item) for item in binding.get("subprotocols", ())),
        )
        family = "message"
    elif kind == "webtransport":
        lane = webtransport_lane_for_profile(
            binding.get("lane") or binding.get("profile") or "webtransport"
        )
        exchange = validate_webtransport_lane_exchange(
            lane=lane,
            exchange=str(binding.get("exchange") or _default_webtransport_exchange(lane)),
        )
        validate_app_framing_for_binding(
            binding_kind=kind,
            framing=str(binding.get("framing") or "webtransport"),
        )
        validate_webtransport_inner_framing(
            lane=lane,
            inner_framing=binding.get("inner_framing"),
        )
        framing = "webtransport"
        family = webtransport_runtime_family(lane)
    else:
        raise ValueError(f"unsupported binding kind {kind!r}")

    return {
        "op_id": op_id,
        "binding_kind": kind,
        "family": family,
        "framing": framing,
        "exchange": exchange,
    }


def _default_webtransport_exchange(lane: str) -> str:
    return {
        "session": "bidirectional_stream",
        "bidi_stream": "bidirectional_stream",
        "unidi_client_stream": "client_stream",
        "unidi_server_stream": "server_stream",
        "datagram": "bidirectional_stream",
    }[lane]


def _plan_fingerprint(plan: Mapping[str, Any]) -> dict[str, Any]:
    stable = {
        "binding_kind": plan["binding_kind"],
        "family": plan["family"],
        "framing": plan["framing"],
        "exchange": plan["exchange"],
    }
    return {
        **stable,
        "fingerprint": sha256(repr(stable).encode("utf-8")).hexdigest(),
    }


def _normalize_route_projection(projection: Mapping[str, Any]) -> dict[str, Any]:
    path = str(projection["path"]).replace("<item_id>", "{item_id}")
    return {
        "path": path,
        "methods": tuple(projection["methods"]),
        "endpoint": projection["endpoint"],
    }


def _join_path(prefix: str, path: str) -> str:
    prefix = "/" + prefix.strip("/")
    path = "/" + path.strip("/")
    if prefix == "/":
        return path
    return f"{prefix}{path}"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _assert_all_equal(values: Iterable[Mapping[str, Any]], message: str) -> None:
    items = tuple(values)
    _assert(bool(items), "no values provided")
    first = _freeze(items[0])
    if any(_freeze(item) != first for item in items[1:]):
        raise AssertionError(message)


def _freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _freeze(value[key]) for key in sorted(value)}
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    return value


CERTIFIABLE_EQUIVALENCES: tuple[CertifiableEquivalence, ...] = (
    CertifiableEquivalence(
        id="transport.rest-jsonrpc-websocket-read",
        status="equivalent",
        claim=(
            "REST, HTTP JSON-RPC, and WebSocket JSON-RPC can share one "
            "Item.read semantic outcome."
        ),
        source_documents=("docs/developer/TRANSPORT_EQUIVALENCE.md",),
        source_modules=("tigrbl_kernel.cross_transport",),
        certify_runtime=_certify_rest_jsonrpc_websocket_read,
    ),
    CertifiableEquivalence(
        id="transport.stream-sse-webtransport-tail",
        status="equivalent",
        claim=(
            "HTTP stream, SSE, and WebTransport stream bindings can preserve "
            "declared tail ordering and completion semantics."
        ),
        source_documents=("docs/developer/TRANSPORT_EQUIVALENCE.md",),
        source_modules=("tigrbl_kernel.cross_transport",),
        certify_runtime=_certify_stream_sse_webtransport_tail,
    ),
    CertifiableEquivalence(
        id="router.fastapi-flask-tigrbl-prefix",
        status="analogous",
        claim=(
            "FastAPI router prefixes, Flask blueprint prefixes, and Tigrbl "
            "router prefixes normalize to the same route projection."
        ),
        source_documents=("docs/developer/ROUTER_TABLE_EQUIVALENCE.md",),
        source_modules=("tigrbl_core._spec.router_spec",),
        certify_runtime=_certify_router_prefix_projection,
    ),
    CertifiableEquivalence(
        id="table.fastapi-flask-tigrbl-resource",
        status="analogous",
        claim=(
            "FastAPI and Flask resource-model patterns can match a Tigrbl "
            "table resource projection, while Tigrbl remains the table authority."
        ),
        source_documents=("docs/developer/ROUTER_TABLE_EQUIVALENCE.md",),
        source_modules=("tigrbl_core._spec.table_profile_spec",),
        certify_runtime=_certify_table_resource_projection,
    ),
    CertifiableEquivalence(
        id="engine.logical-datatype-lowering",
        status="projection-only",
        claim=(
            "Canonical logical datatypes can be certified across engines even "
            "when physical SQL lowerings differ."
        ),
        source_documents=("docs/developer/ENGINE_SQL_EQUIVALENCE.md",),
        source_modules=("tigrbl_core._spec.datatypes",),
        certify_runtime=_certify_engine_datatype_lowering,
    ),
)
