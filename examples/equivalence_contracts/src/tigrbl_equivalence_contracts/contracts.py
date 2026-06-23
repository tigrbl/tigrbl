from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

EquivalenceStatus = Literal[
    "equivalent",
    "analogous",
    "projection-only",
    "tigrbl-specific",
    "not-equivalent",
]

FrameworkName = Literal["tigrbl", "fastapi", "flask"]


@dataclass(frozen=True)
class FrameworkImplementation:
    framework: FrameworkName
    code_ref: str
    build: Callable[[], Any]
    exercise: Callable[[Any], Any]
    normalize: Callable[[Any], Any]

    def certify(self) -> Any:
        return self.normalize(self.exercise(self.build()))


@dataclass(frozen=True)
class CertificationResult:
    equivalence_id: str
    status: EquivalenceStatus
    certified: bool
    evidence: Mapping[str, Any]


@dataclass(frozen=True)
class CertifiableEquivalence:
    id: str
    category: str
    intent: str
    status: EquivalenceStatus
    claim: str
    source_documents: tuple[str, ...]
    implementations: tuple[FrameworkImplementation, ...]

    def certify(self) -> CertificationResult:
        observed = {
            implementation.framework: implementation.certify()
            for implementation in self.implementations
        }
        _assert_all_equal(observed.values(), f"{self.id} implementations diverged")
        return CertificationResult(
            equivalence_id=self.id,
            status=self.status,
            certified=True,
            evidence={
                "category": self.category,
                "intent": self.intent,
                "observed": observed,
                "code_refs": {
                    implementation.framework: implementation.code_ref
                    for implementation in self.implementations
                },
            },
        )


def equivalence_by_id(equivalence_id: str) -> CertifiableEquivalence:
    for case in CERTIFIABLE_EQUIVALENCES:
        if case.id == equivalence_id:
            return case
    raise KeyError(equivalence_id)


def certify_all() -> tuple[CertificationResult, ...]:
    return tuple(case.certify() for case in CERTIFIABLE_EQUIVALENCES)


def matrix_rows() -> tuple[dict[str, str], ...]:
    rows: list[dict[str, str]] = []
    for case in CERTIFIABLE_EQUIVALENCES:
        refs = {item.framework: item.code_ref for item in case.implementations}
        rows.append(
            {
                "id": case.id,
                "category": case.category,
                "intent": case.intent,
                "status": case.status,
                "tigrbl": refs["tigrbl"],
                "fastapi": refs["fastapi"],
                "flask": refs["flask"],
                "test": "examples/equivalence_contracts/tests/test_certifiable_equivalences.py",
            }
        )
    return tuple(rows)


def _impl(
    framework: FrameworkName,
    code_ref: str,
    build: Callable[[], Any],
    exercise: Callable[[Any], Any],
    normalize: Callable[[Any], Any],
) -> FrameworkImplementation:
    return FrameworkImplementation(
        framework=framework,
        code_ref=code_ref,
        build=build,
        exercise=exercise,
        normalize=normalize,
    )


def _http_get(path: str) -> tuple[FrameworkImplementation, ...]:
    tigrbl_builder = "build_health_app" if path == "/health" else "build_router_app"
    fastapi_builder = "build_health_app" if path == "/health" else "build_router_app"
    flask_builder = "build_health_app" if path == "/health" else "build_router_app"
    return (
        _impl(
            "tigrbl",
            "src/tigrbl_equivalence_contracts/frameworks/tigrbl_impl.py",
            _lazy_builder("tigrbl_impl", tigrbl_builder),
            lambda app: _runtime_call("call_asgi_get", app, path),
            lambda result: _runtime_call("normalize_http_result", result),
        ),
        _impl(
            "fastapi",
            "src/tigrbl_equivalence_contracts/frameworks/fastapi_impl.py",
            _lazy_builder("fastapi_impl", fastapi_builder),
            lambda app: _runtime_call("call_asgi_get", app, path),
            lambda result: _runtime_call("normalize_http_result", result),
        ),
        _impl(
            "flask",
            "src/tigrbl_equivalence_contracts/frameworks/flask_impl.py",
            _lazy_builder("flask_impl", flask_builder),
            lambda app: _runtime_call("call_flask_get", app, path),
            lambda result: _runtime_call("normalize_http_result", result),
        ),
    )


def _projection_case(
    tigrbl_builder: str,
    fastapi_builder: str,
    flask_builder: str,
) -> tuple[FrameworkImplementation, ...]:
    return (
        _impl(
            "tigrbl",
            "src/tigrbl_equivalence_contracts/frameworks/tigrbl_impl.py",
            _lazy_builder("tigrbl_impl", tigrbl_builder),
            lambda value: value,
            lambda result: _runtime_call("normalize_projection", result),
        ),
        _impl(
            "fastapi",
            "src/tigrbl_equivalence_contracts/frameworks/fastapi_impl.py",
            _lazy_builder("fastapi_impl", fastapi_builder),
            lambda value: value,
            lambda result: _runtime_call("normalize_projection", result),
        ),
        _impl(
            "flask",
            "src/tigrbl_equivalence_contracts/frameworks/flask_impl.py",
            _lazy_builder("flask_impl", flask_builder),
            lambda value: value,
            lambda result: _runtime_call("normalize_projection", result),
        ),
    )


def _runtime_call(attr_name: str, *args: Any) -> Any:
    module = import_module("tigrbl_equivalence_contracts.runtime")
    return getattr(module, attr_name)(*args)


def _lazy_builder(module_name: str, attr_name: str) -> Callable[[], Any]:
    def _build() -> Any:
        module = import_module(
            f"tigrbl_equivalence_contracts.frameworks.{module_name}"
        )
        return getattr(module, attr_name)()

    return _build


def _assert_all_equal(values: Any, message: str) -> None:
    items = tuple(values)
    if not items:
        raise AssertionError("no implementation evidence produced")
    first = items[0]
    if any(item != first for item in items[1:]):
        raise AssertionError(f"{message}: {items!r}")


CERTIFIABLE_EQUIVALENCES: tuple[CertifiableEquivalence, ...] = (
    CertifiableEquivalence(
        id="app.http-health",
        category="application",
        intent="Author a simple GET endpoint returning a stable JSON payload.",
        status="equivalent",
        claim="TigrblApp, FastAPI, and Flask can expose the same HTTP GET behavior.",
        source_documents=("docs/developer/AUTHORING_EQUIVALENCE.md",),
        implementations=_http_get("/health"),
    ),
    CertifiableEquivalence(
        id="router.prefix-read",
        category="router",
        intent="Group a read endpoint under a versioned router or blueprint prefix.",
        status="analogous",
        claim="TigrblRouter, FastAPI APIRouter, and Flask Blueprint prefixes can project the same read route behavior.",
        source_documents=("docs/developer/ROUTER_TABLE_EQUIVALENCE.md",),
        implementations=_http_get("/v1/items/item-1"),
    ),
    CertifiableEquivalence(
        id="table.resource-contract",
        category="table",
        intent="Declare an Item resource with id/name fields and create/list/read operations.",
        status="analogous",
        claim="FastAPI and Flask resource patterns can match the same resource projection as a Tigrbl table profile.",
        source_documents=("docs/developer/ROUTER_TABLE_EQUIVALENCE.md",),
        implementations=_projection_case(
            "build_table_projection",
            "build_table_projection",
            "build_table_projection",
        ),
    ),
    CertifiableEquivalence(
        id="websocket.echo-contract",
        category="transport",
        intent="Declare a WebSocket echo channel with JSON text framing.",
        status="projection-only",
        claim="Tigrbl, FastAPI, and Flask extension-style WebSocket declarations can project the same channel contract.",
        source_documents=("docs/developer/TRANSPORT_EQUIVALENCE.md",),
        implementations=_projection_case(
            "build_websocket_projection",
            "build_websocket_projection",
            "build_websocket_projection",
        ),
    ),
    CertifiableEquivalence(
        id="sql.logical-datatype-lowering",
        category="sql",
        intent="Track logical field types separately from engine-specific SQL lowerings.",
        status="projection-only",
        claim="Each framework-facing table shape can preserve the same logical datatype contract while SQL physical names vary by engine.",
        source_documents=("docs/developer/ENGINE_SQL_EQUIVALENCE.md",),
        implementations=_projection_case(
            "build_sql_projection",
            "build_sql_projection",
            "build_sql_projection",
        ),
    ),
)
