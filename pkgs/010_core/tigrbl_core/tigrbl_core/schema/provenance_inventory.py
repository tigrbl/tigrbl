"""Inventory-backed surface provenance chains."""

from __future__ import annotations

import json
from dataclasses import dataclass
from importlib import resources
from pathlib import Path
from typing import Any, Mapping

from .provenance import (
    SurfaceDependencyEdge,
    SurfaceProvenanceChain,
    SurfaceProvenanceNode,
)

MATRIX_COLUMNS: tuple[str, ...] = (
    "Spec",
    "JSON schema",
    "Dataclass",
    "Base",
    "Concrete(s)",
    "Mount",
    "Include",
    "Include bulk",
    "Class collection",
    "Shortcut(s)",
    "Decorator(s)",
    "define_*",
    "derive_*",
    "make_*",
)

RELATION_DIRECTIONS: Mapping[str, tuple[str, str]] = {
    "json_schema_of": ("json_schema", "spec_dataclass"),
    "base_for": ("base_contract", "concrete"),
    "constructs": ("construction", "concrete"),
    "constructs_spec": ("construction", "spec_dataclass"),
    "exports": ("public_surface", "construction"),
    "collects": ("collection", "concrete"),
    "projects_to_runtime": ("compiled_projection", "runtime_behavior"),
    "verified_by": ("runtime_behavior", "verification"),
}


@dataclass(frozen=True)
class SurfaceInventoryRow:
    """One authoritative row in the spec/surface provenance inventory."""

    id: str
    matrix: Mapping[str, str]
    disposition: str
    partial_reasons: tuple[str, ...] = ()

    @property
    def surface(self) -> str:
        spec = _clean_cell(self.matrix["Spec"])
        if spec != "missing":
            return spec
        for column in MATRIX_COLUMNS[1:]:
            values = _cell_values(self.matrix[column])
            if values:
                return values[0]
        return self.id

    @property
    def signature(self) -> tuple[str, ...]:
        return tuple(self.matrix[column] for column in MATRIX_COLUMNS)

    def to_chain(self) -> SurfaceProvenanceChain:
        nodes: list[SurfaceProvenanceNode] = []
        seen: set[str] = set()

        def add(stage: str, name: str, *, kind: str | None = None) -> None:
            if name in seen:
                return
            seen.add(name)
            nodes.append(SurfaceProvenanceNode(stage, name, kind=kind))  # type: ignore[arg-type]

        spec = _clean_cell(self.matrix["Spec"])
        schema = _clean_cell(self.matrix["JSON schema"])
        if schema == "generated" and spec != "missing":
            add("json_schema", f"{spec}.json")
        elif schema.startswith("schemas/"):
            add("json_schema", schema)
        else:
            add("json_schema", "missing")

        if spec != "missing":
            add("spec_dataclass", spec)

        for value in _cell_values(self.matrix["Base"]):
            add("base_contract", value)
        for value in _cell_values(self.matrix["Concrete(s)"]):
            add("concrete", value)

        construction_nodes: list[tuple[str, str]] = []
        public_nodes: list[str] = []
        for column, kind in (
            ("Mount", "factory"),
            ("Include", "factory"),
            ("Include bulk", "factory"),
            ("Shortcut(s)", "shortcut"),
            ("Decorator(s)", "decorator"),
            ("define_*", "factory"),
            ("derive_*", "factory"),
            ("make_*", "make"),
        ):
            for value in _cell_values(self.matrix[column]):
                if value.startswith("tigrbl."):
                    public_nodes.append(value)
                else:
                    construction_nodes.append((value, kind))

        for value, kind in construction_nodes:
            add("construction", value, kind=kind)
        for value in public_nodes:
            add("public_surface", value)

        for value in _cell_values(self.matrix["Class collection"]):
            add("collection", value)

        projection_name = f"{self.surface} compiled projection"
        runtime_name = f"{self.surface} runtime behavior"
        verification_name = "tst:surface-provenance-chain-t2-contract"
        add("compiled_projection", projection_name)
        add("runtime_behavior", runtime_name)
        add("verification", verification_name)

        return SurfaceProvenanceChain(
            surface=self.surface,
            nodes=tuple(nodes),
            dependencies=_derive_dependencies(nodes),
            allow_missing_json_schema=True,
        )


def load_surface_provenance_inventory(
    path: str | Path | None = None,
) -> tuple[SurfaceInventoryRow, ...]:
    """Load the package surface provenance inventory."""

    if path is None:
        text = resources.files(__package__).joinpath(
            "surface_chains.json"
        ).read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    payload = json.loads(text)
    return tuple(
        SurfaceInventoryRow(
            id=item["id"],
            matrix=item["matrix"],
            disposition=item["disposition"],
            partial_reasons=tuple(item.get("partial_reasons", ())),
        )
        for item in payload["rows"]
    )


def inventory_matrix_signatures(
    rows: tuple[SurfaceInventoryRow, ...],
) -> set[tuple[str, ...]]:
    return {row.signature for row in rows}


def _derive_dependencies(
    nodes: list[SurfaceProvenanceNode],
) -> tuple[SurfaceDependencyEdge, ...]:
    by_stage: dict[str, list[SurfaceProvenanceNode]] = {}
    for node in nodes:
        by_stage.setdefault(node.stage, []).append(node)

    edges: list[SurfaceDependencyEdge] = []

    def first(stage: str) -> SurfaceProvenanceNode | None:
        values = by_stage.get(stage, ())
        return values[0] if values else None

    schema = first("json_schema")
    spec = first("spec_dataclass")
    if schema and spec and schema.name != "missing":
        edges.append(SurfaceDependencyEdge(schema.name, spec.name, "json_schema_of"))

    concrete = first("concrete")
    for base in by_stage.get("base_contract", ()):
        if concrete:
            edges.append(SurfaceDependencyEdge(base.name, concrete.name, "base_for"))

    construction_target = concrete or spec
    for construction in by_stage.get("construction", ()):
        if construction_target:
            edges.append(
                SurfaceDependencyEdge(
                    construction.name,
                    construction_target.name,
                    "constructs" if concrete else "constructs_spec",
                )
            )

    public_target = first("construction") or concrete or spec
    for public in by_stage.get("public_surface", ()):
        if public_target and public.name != public_target.name:
            edges.append(SurfaceDependencyEdge(public.name, public_target.name, "exports"))

    collection_target = concrete or spec
    for collection in by_stage.get("collection", ()):
        if collection_target:
            edges.append(
                SurfaceDependencyEdge(collection.name, collection_target.name, "collects")
            )

    projection = first("compiled_projection")
    runtime = first("runtime_behavior")
    verification = first("verification")
    if projection and runtime:
        edges.append(
            SurfaceDependencyEdge(
                projection.name,
                runtime.name,
                "projects_to_runtime",
            )
        )
    if runtime and verification:
        edges.append(
            SurfaceDependencyEdge(runtime.name, verification.name, "verified_by")
        )

    return tuple(edges)


def _cell_values(cell: str) -> tuple[str, ...]:
    clean = _clean_cell(cell)
    if clean in {"n/a", "none", "none; missing spec", "no", "no, ABC", "yes"}:
        return ()
    return tuple(part.strip() for part in clean.split(",") if part.strip())


def _clean_cell(cell: str) -> str:
    return cell.replace("`", "").strip()


__all__ = [
    "MATRIX_COLUMNS",
    "RELATION_DIRECTIONS",
    "SurfaceInventoryRow",
    "inventory_matrix_signatures",
    "load_surface_provenance_inventory",
]
