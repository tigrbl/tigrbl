"""The equivalence matrix that points human readers at runnable examples.

The implementation files are deliberately ordinary framework code.  This
module records which framework examples should be compared, which documents
they support, and which shared runtime lesson certifies their HTTP behavior.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

from .runtime import ServerKind, assert_widget_rest_crud_over_http

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
    """One framework entry in an equivalence row."""

    framework: FrameworkName
    code_ref: str
    app: Callable[[], Any]
    server_kind: ServerKind
    exercise: Callable[[Any, ServerKind], Any]
    normalize: Callable[[Any], Any]

    def certify(self) -> Any:
        """Serve the framework app and return normalized proof evidence."""

        return self.normalize(self.exercise(self.app(), self.server_kind))


@dataclass(frozen=True)
class CertificationResult:
    """The evidence produced after one equivalence row has been certified."""

    equivalence_id: str
    status: EquivalenceStatus
    certified: bool
    evidence: Mapping[str, Any]


@dataclass(frozen=True)
class CertifiableEquivalence:
    """A row in the technical-marketing equivalence matrix.

    Each row names the developer intent, points at source files for visual
    inspection, and runs the same client-side assertions against every listed
    framework implementation.
    """

    id: str
    category: str
    intent: str
    status: EquivalenceStatus
    claim: str
    source_documents: tuple[str, ...]
    implementations: tuple[FrameworkImplementation, ...]

    def certify(self) -> CertificationResult:
        """Run every implementation and fail if any observed result differs."""

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
    """Return one equivalence row by its stable matrix identifier."""

    for case in CERTIFIABLE_EQUIVALENCES:
        if case.id == equivalence_id:
            return case
    raise KeyError(equivalence_id)


def certify_all() -> tuple[CertificationResult, ...]:
    """Certify every declared equivalence row."""

    return tuple(case.certify() for case in CERTIFIABLE_EQUIVALENCES)


def matrix_rows() -> tuple[dict[str, str], ...]:
    """Render the rows used by generated documentation tables."""

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
    app: Callable[[], Any],
    server_kind: ServerKind,
    exercise: Callable[[Any, ServerKind], Any],
    normalize: Callable[[Any], Any],
) -> FrameworkImplementation:
    return FrameworkImplementation(
        framework=framework,
        code_ref=code_ref,
        app=app,
        server_kind=server_kind,
        exercise=exercise,
        normalize=normalize,
    )


def _rest_crud_case(
    tigrbl_attr: str,
    fastapi_attr: str,
    flask_attr: str,
) -> tuple[FrameworkImplementation, ...]:
    return (
        _impl(
            "tigrbl",
            "src/tigrbl_equivalence_contracts/frameworks/tigrbl_impl.py",
            _lazy_attr("tigrbl_impl", tigrbl_attr),
            "asgi",
            assert_widget_rest_crud_over_http,
            lambda result: result,
        ),
        _impl(
            "fastapi",
            "src/tigrbl_equivalence_contracts/frameworks/fastapi_impl.py",
            _lazy_attr("fastapi_impl", fastapi_attr),
            "asgi",
            assert_widget_rest_crud_over_http,
            lambda result: result,
        ),
        _impl(
            "flask",
            "src/tigrbl_equivalence_contracts/frameworks/flask_impl.py",
            _lazy_attr("flask_impl", flask_attr),
            "wsgi",
            assert_widget_rest_crud_over_http,
            lambda result: result,
        ),
    )


def _lazy_attr(module_name: str, attr_name: str) -> Callable[[], Any]:
    """Load a framework app only during certification."""

    def _get() -> Any:
        module = import_module(
            f"tigrbl_equivalence_contracts.frameworks.{module_name}"
        )
        return getattr(module, attr_name)

    return _get


def _assert_all_equal(values: Any, message: str) -> None:
    """Assert that every framework produced byte-for-byte equivalent evidence."""

    items = tuple(values)
    if not items:
        raise AssertionError("no implementation evidence produced")
    first = items[0]
    if any(item != first for item in items[1:]):
        raise AssertionError(f"{message}: {items!r}")


CERTIFIABLE_EQUIVALENCES: tuple[CertifiableEquivalence, ...] = (
    CertifiableEquivalence(
        id="rest-crud.widget",
        category="rest-crud",
        intent="Author REST CRUD for a Widget resource with id and name columns.",
        status="analogous",
        claim="Tigrbl RestTable, FastAPI routes, and Flask routes can expose the same Widget REST CRUD surface.",
        source_documents=(
            "docs/developer/AUTHORING_EQUIVALENCE.md",
            "docs/developer/ROUTER_TABLE_EQUIVALENCE.md",
        ),
        implementations=_rest_crud_case(
            "app",
            "app",
            "app",
        ),
    ),
)
