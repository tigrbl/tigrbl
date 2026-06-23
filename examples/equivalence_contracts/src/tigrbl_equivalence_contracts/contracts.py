"""The equivalence matrix that points human readers at runnable examples."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

from .runtime import ServerKind

EquivalenceStatus = Literal["equivalent", "analogous", "projection-only", "tigrbl-specific", "not-equivalent"]
FrameworkName = Literal["tigrbl", "fastapi", "flask"]


@dataclass(frozen=True)
class FrameworkImplementation:
    """One framework entry in an equivalence row."""

    framework: FrameworkName
    code_ref: str
    app: Callable[[], Any]
    server_kind: ServerKind
    exercise: Callable[..., Any]
    exercise_args: tuple[Any, ...]
    normalize: Callable[[Any], Any]

    def certify(self) -> Any:
        """Serve the framework app and return normalized proof evidence."""

        return self.normalize(self.exercise(self.app(), self.server_kind, *self.exercise_args))


@dataclass(frozen=True)
class CertificationResult:
    """The evidence produced after one equivalence row has been certified."""

    equivalence_id: str
    status: EquivalenceStatus
    certified: bool
    evidence: Mapping[str, Any]


@dataclass(frozen=True)
class CertifiableEquivalence:
    """A row in the technical-marketing equivalence matrix."""

    id: str
    category: str
    intent: str
    status: EquivalenceStatus
    claim: str
    source_documents: tuple[str, ...]
    implementations: tuple[FrameworkImplementation, ...]

    def certify(self) -> CertificationResult:
        """Run every implementation and fail if any observed result differs."""

        observed = {implementation.framework: implementation.certify() for implementation in self.implementations}
        _assert_all_equal(observed.values(), f"{self.id} implementations diverged")
        return CertificationResult(
            equivalence_id=self.id,
            status=self.status,
            certified=True,
            evidence={
                "category": self.category,
                "intent": self.intent,
                "observed": observed,
                "code_refs": {implementation.framework: implementation.code_ref for implementation in self.implementations},
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
        rows.append({
            "id": case.id,
            "category": case.category,
            "intent": case.intent,
            "status": case.status,
            "tigrbl": refs["tigrbl"],
            "fastapi": refs["fastapi"],
            "flask": refs["flask"],
            "test": "examples/equivalence_contracts/tests/test_certifiable_equivalences.py",
        })
    return tuple(rows)


def _impl(
    framework: FrameworkName,
    code_ref: str,
    app: Callable[[], Any],
    server_kind: ServerKind,
    exercise: Callable[..., Any],
    exercise_args: tuple[Any, ...],
    normalize: Callable[[Any], Any],
) -> FrameworkImplementation:
    return FrameworkImplementation(framework, code_ref, app, server_kind, exercise, exercise_args, normalize)


def _lazy_attr(module_name: str, attr_name: str) -> Callable[[], Any]:
    """Load an equivalence app only during certification."""

    def _get() -> Any:
        module = import_module(f"tigrbl_equivalence_contracts.{module_name}")
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


_CONTRACT_MODULES = ('equivalences.rest_crud_widget.contract', 'equivalences.table_base.contract', 'equivalences.rest_table.contract', 'equivalences.json_rpc_table.contract', 'equivalences.rest_json_rpc_table.contract', 'equivalences.bulk_crud_table.contract', 'equivalences.rest_oltp_table.contract', 'equivalences.oltp_table.contract', 'equivalences.json_rpc_oltp_table.contract', 'equivalences.rest_json_rpc_oltp_table.contract', 'equivalences.rest_olap_table.contract', 'equivalences.olap_table.contract', 'equivalences.json_rpc_olap_table.contract', 'equivalences.rest_json_rpc_olap_table.contract', 'equivalences.stream_table.contract', 'equivalences.sse_table.contract', 'equivalences.event_stream_table.contract', 'equivalences.web_socket_table.contract', 'equivalences.web_socket_json_rpc_table.contract', 'equivalences.web_transport_table.contract', 'equivalences.web_transport_bidi_table.contract', 'equivalences.web_transport_client_stream_table.contract', 'equivalences.web_transport_server_stream_table.contract', 'equivalences.web_transport_datagram_table.contract')


def _load_contracts() -> tuple[CertifiableEquivalence, ...]:
    return tuple(import_module(f"tigrbl_equivalence_contracts.{module_name}").CONTRACT for module_name in _CONTRACT_MODULES)


CERTIFIABLE_EQUIVALENCES: tuple[CertifiableEquivalence, ...] = _load_contracts()
