"""Surface provenance chain validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Literal, Sequence

ProvenanceStage = Literal[
    "json_schema",
    "spec_dataclass",
    "base_contract",
    "concrete",
    "construction",
    "public_surface",
    "collection",
    "compiled_projection",
    "runtime_behavior",
    "verification",
]

ConstructionKind = Literal["make", "factory", "shortcut", "decorator", "import"]

_ORDER: tuple[ProvenanceStage, ...] = (
    "json_schema",
    "spec_dataclass",
    "base_contract",
    "concrete",
    "construction",
    "public_surface",
    "collection",
    "compiled_projection",
    "runtime_behavior",
    "verification",
)

_ORDER_INDEX = {stage: index for index, stage in enumerate(_ORDER)}


@dataclass(frozen=True)
class SurfaceProvenanceNode:
    """One named artifact in a public-surface provenance chain."""

    stage: ProvenanceStage
    name: str
    kind: ConstructionKind | None = None


@dataclass(frozen=True)
class SurfaceDependencyEdge:
    """A directed dependency between two named provenance nodes."""

    source: str
    target: str
    relation: str


@dataclass(frozen=True)
class SurfaceProvenanceChain:
    """JSON-schema-first provenance declaration for a public surface."""

    surface: str
    nodes: tuple[SurfaceProvenanceNode, ...]
    dependencies: tuple[SurfaceDependencyEdge, ...] = field(default_factory=tuple)
    allow_missing_json_schema: bool = False


@dataclass(frozen=True)
class SurfaceProvenanceReport:
    """Validation result for a surface provenance chain."""

    surface: str
    passed: bool
    errors: tuple[str, ...]


class SurfaceProvenanceError(ValueError):
    """Raised when strict surface provenance validation fails."""


def validate_surface_provenance_chain(
    chain: SurfaceProvenanceChain,
    *,
    strict: bool = True,
) -> SurfaceProvenanceReport:
    """Validate lineage, provenance, and dependency edges for one surface.

    T0 is covered by artifact presence and dependency resolution. T1 is covered
    by JSON-schema-first ordering. T2 is covered by fail-closed validation of
    duplicate nodes, dangling dependencies, and construction-kind semantics.
    """

    errors = tuple(_validate(chain))
    report = SurfaceProvenanceReport(
        surface=chain.surface,
        passed=not errors,
        errors=errors,
    )
    if strict and errors:
        raise SurfaceProvenanceError("; ".join(errors))
    return report


def validate_surface_provenance_chains(
    chains: Iterable[SurfaceProvenanceChain],
    *,
    strict: bool = True,
) -> tuple[SurfaceProvenanceReport, ...]:
    """Validate multiple surface provenance chains."""

    reports = tuple(
        validate_surface_provenance_chain(chain, strict=False) for chain in chains
    )
    errors = [
        f"{report.surface}: {error}"
        for report in reports
        for error in report.errors
    ]
    if strict and errors:
        raise SurfaceProvenanceError("; ".join(errors))
    return reports


def _validate(chain: SurfaceProvenanceChain) -> Sequence[str]:
    errors: list[str] = []
    if not chain.surface:
        errors.append("surface must be non-empty")
    if not chain.nodes:
        errors.append("chain must declare at least one node")
        return errors

    names = [node.name for node in chain.nodes]
    if any(not name for name in names):
        errors.append("node names must be non-empty")

    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        errors.append(f"duplicate provenance nodes: {', '.join(duplicates)}")

    first = chain.nodes[0]
    if first.stage != "json_schema":
        errors.append("first provenance node must be a JSON Schema")
    if first.stage == "json_schema" and first.name == "missing":
        if not chain.allow_missing_json_schema:
            errors.append("missing JSON Schema requires allow_missing_json_schema")

    last_order = -1
    for node in chain.nodes:
        order = _ORDER_INDEX[node.stage]
        if order < last_order:
            errors.append(f"{node.name} is out of provenance order")
        last_order = max(last_order, order)
        if node.kind == "make" and not node.name.startswith("make"):
            errors.append(f"{node.name} is not a make construction surface")
        if node.kind is not None and node.stage != "construction":
            errors.append(f"{node.name} has construction kind outside construction")

    known = set(names)
    for edge in chain.dependencies:
        if edge.source not in known:
            errors.append(f"dependency source is not declared: {edge.source}")
        if edge.target not in known:
            errors.append(f"dependency target is not declared: {edge.target}")
        if not edge.relation:
            errors.append(f"dependency relation is empty: {edge.source}->{edge.target}")

    return errors


__all__ = [
    "SurfaceDependencyEdge",
    "SurfaceProvenanceChain",
    "SurfaceProvenanceError",
    "SurfaceProvenanceNode",
    "SurfaceProvenanceReport",
    "validate_surface_provenance_chain",
    "validate_surface_provenance_chains",
]
