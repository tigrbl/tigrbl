from __future__ import annotations

import pytest

from tigrbl_core.schema import (
    SurfaceDependencyEdge,
    SurfaceProvenanceChain,
    SurfaceProvenanceError,
    SurfaceProvenanceNode,
    validate_surface_provenance_chain,
    validate_surface_provenance_chains,
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
    assert report.warnings == ()


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


def test_surface_provenance_t2_warns_for_dangling_dependency_edges() -> None:
    chain = SurfaceProvenanceChain(
        surface="Schema",
        nodes=(
            SurfaceProvenanceNode("json_schema", "SchemaSpec.json"),
            SurfaceProvenanceNode("spec_dataclass", "SchemaSpec"),
        ),
        dependencies=(
            SurfaceDependencyEdge("SchemaSpec.json", "Schema", "json_schema_of"),
        ),
    )

    report = validate_surface_provenance_chain(chain)

    assert report.passed is True
    assert report.errors == ()
    assert "dependency target is not declared: Schema" in report.warnings


def test_surface_provenance_t2_rejects_factory_in_make_column() -> None:
    chain = SurfaceProvenanceChain(
        surface="Schema",
        nodes=(
            SurfaceProvenanceNode("json_schema", "SchemaSpec.json"),
            SurfaceProvenanceNode("spec_dataclass", "SchemaSpec"),
            SurfaceProvenanceNode("construction", "schema", kind="make"),
        ),
    )

    with pytest.raises(SurfaceProvenanceError, match="not a make"):
        validate_surface_provenance_chain(chain)


def test_surface_provenance_t2_accepts_actual_make_constructor() -> None:
    chain = SurfaceProvenanceChain(
        surface="Column",
        nodes=(
            SurfaceProvenanceNode("json_schema", "ColumnSpec.json"),
            SurfaceProvenanceNode("spec_dataclass", "ColumnSpec"),
            SurfaceProvenanceNode("base_contract", "ColumnBase"),
            SurfaceProvenanceNode("concrete", "Column"),
            SurfaceProvenanceNode("construction", "makeColumn", kind="make"),
            SurfaceProvenanceNode("public_surface", "tigrbl.shortcuts.column"),
            SurfaceProvenanceNode(
                "verification",
                "tst:surface-provenance-chain-t2-contract",
            ),
        ),
    )

    report = validate_surface_provenance_chain(chain)

    assert report.passed is True
    assert report.errors == ()
    assert "provenance stage is not declared: collection" in report.warnings


def test_surface_provenance_t2_reports_all_chain_errors() -> None:
    reports = validate_surface_provenance_chains(
        (
            _schema_chain(),
            SurfaceProvenanceChain(
                surface="OAuth2",
                nodes=(
                    SurfaceProvenanceNode("json_schema", "missing"),
                    SurfaceProvenanceNode("concrete", "OAuth2"),
                    SurfaceProvenanceNode("concrete", "OAuth2"),
                ),
            ),
        ),
        strict=False,
    )

    assert reports[0].passed is True
    assert reports[1].passed is False
    assert "missing JSON Schema" in "; ".join(reports[1].warnings)
    assert "duplicate provenance nodes" in "; ".join(reports[1].errors)


def test_surface_provenance_t2_rejects_out_of_order_existing_nodes() -> None:
    chain = SurfaceProvenanceChain(
        surface="Column",
        nodes=(
            SurfaceProvenanceNode("json_schema", "ColumnSpec.json"),
            SurfaceProvenanceNode("concrete", "Column"),
            SurfaceProvenanceNode("base_contract", "ColumnBase"),
        ),
    )

    with pytest.raises(SurfaceProvenanceError, match="out of provenance order"):
        validate_surface_provenance_chain(chain)
