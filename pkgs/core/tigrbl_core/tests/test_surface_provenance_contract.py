from __future__ import annotations

import pytest

from tigrbl_core.schema import (
    SurfaceDependencyEdge,
    SurfaceProvenanceChain,
    SurfaceProvenanceError,
    SurfaceProvenanceNode,
    validate_surface_provenance_chain,
)


def _schema_chain() -> SurfaceProvenanceChain:
    return SurfaceProvenanceChain(
        surface="Schema",
        nodes=(
            SurfaceProvenanceNode("json_schema", "SchemaSpec.json"),
            SurfaceProvenanceNode("spec_dataclass", "SchemaSpec"),
            SurfaceProvenanceNode("base_contract", "SchemaBase"),
            SurfaceProvenanceNode("concrete", "Schema"),
            SurfaceProvenanceNode("construction", "schema_spec", kind="factory"),
            SurfaceProvenanceNode("construction", "schema", kind="factory"),
            SurfaceProvenanceNode("public_surface", "tigrbl.shortcuts.schema"),
            SurfaceProvenanceNode("collection", "SCHEMAS"),
            SurfaceProvenanceNode("compiled_projection", "compiled schema projection"),
            SurfaceProvenanceNode("runtime_behavior", "runtime schema use"),
            SurfaceProvenanceNode(
                "verification",
                "tst:surface-provenance-chain-t0-t1-contract",
            ),
        ),
        dependencies=(
            SurfaceDependencyEdge("SchemaSpec.json", "SchemaSpec", "json_schema_of"),
            SurfaceDependencyEdge("SchemaBase", "Schema", "base_for"),
            SurfaceDependencyEdge("schema", "Schema", "constructs"),
            SurfaceDependencyEdge("SCHEMAS", "Schema", "collects"),
        ),
    )


def test_surface_provenance_t0_t1_accepts_json_schema_first_chain() -> None:
    report = validate_surface_provenance_chain(_schema_chain())

    assert report.passed is True
    assert report.errors == ()


def test_surface_provenance_t1_rejects_non_schema_first_lineage() -> None:
    chain = SurfaceProvenanceChain(
        surface="Schema",
        nodes=(
            SurfaceProvenanceNode("spec_dataclass", "SchemaSpec"),
            SurfaceProvenanceNode("json_schema", "SchemaSpec.json"),
        ),
    )

    with pytest.raises(SurfaceProvenanceError, match="first provenance node"):
        validate_surface_provenance_chain(chain)
