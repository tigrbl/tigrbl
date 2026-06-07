from __future__ import annotations

import json
from pathlib import Path

import pytest

from tigrbl_core.schema import (
    MATRIX_COLUMNS,
    RELATION_DIRECTIONS,
    SurfaceInventoryRow,
    inventory_matrix_signatures,
    load_surface_provenance_inventory,
    validate_surface_provenance_chain,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
MATRIX_PATH = REPO_ROOT / "docs" / "spec-surface-matrix.md"
SCHEMA_ROOT = REPO_ROOT / "pkgs" / "core" / "tigrbl_core" / "schemas"
REGISTRY_PATH = REPO_ROOT / ".ssot" / "registry.json"


def _matrix_signatures() -> set[tuple[str, ...]]:
    signatures: set[tuple[str, ...]] = set()
    for line in MATRIX_PATH.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `") and not line.startswith("| missing"):
            continue
        cells = tuple(part.strip() for part in line.strip().strip("|").split("|"))
        assert len(cells) == len(MATRIX_COLUMNS), line
        signatures.add(cells)
    return signatures


def _node_stage(chain, name: str) -> str:
    for node in chain.nodes:
        if node.name == name:
            return node.stage
    raise AssertionError(f"node is not declared: {name}")


@pytest.fixture(scope="module")
def inventory() -> tuple[SurfaceInventoryRow, ...]:
    return load_surface_provenance_inventory()


def test_surface_provenance_inventory_t0_covers_every_matrix_row(
    inventory: tuple[SurfaceInventoryRow, ...],
) -> None:
    assert inventory
    assert inventory_matrix_signatures(inventory) == _matrix_signatures()


def test_surface_provenance_inventory_t0_has_stable_unique_row_ids(
    inventory: tuple[SurfaceInventoryRow, ...],
) -> None:
    ids = [row.id for row in inventory]

    assert ids == sorted(ids)
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize("row", load_surface_provenance_inventory(), ids=lambda row: row.id)
def test_surface_provenance_inventory_t1_validates_every_declared_chain(
    row: SurfaceInventoryRow,
) -> None:
    report = validate_surface_provenance_chain(row.to_chain(), strict=False)

    assert report.errors == ()
    if row.disposition == "complete":
        assert report.warnings == ()
        assert row.partial_reasons == ()
    else:
        assert row.partial_reasons


@pytest.mark.parametrize("row", load_surface_provenance_inventory(), ids=lambda row: row.id)
def test_surface_provenance_inventory_t1_resolves_declared_json_schema_artifacts(
    row: SurfaceInventoryRow,
) -> None:
    schema_cell = row.matrix["JSON schema"].replace("`", "").strip()
    spec = row.matrix["Spec"].replace("`", "").strip()

    if schema_cell == "generated":
        assert (SCHEMA_ROOT / f"{spec}.json").is_file()
    elif schema_cell.startswith("schemas/"):
        assert (REPO_ROOT / "pkgs" / "core" / "tigrbl_core" / schema_cell).is_file()


@pytest.mark.parametrize("row", load_surface_provenance_inventory(), ids=lambda row: row.id)
def test_surface_provenance_inventory_t2_dependency_edges_are_directional(
    row: SurfaceInventoryRow,
) -> None:
    chain = row.to_chain()

    for edge in chain.dependencies:
        assert edge.relation in RELATION_DIRECTIONS
        source_stage, target_stage = RELATION_DIRECTIONS[edge.relation]
        assert _node_stage(chain, edge.source) == source_stage
        assert _node_stage(chain, edge.target) == target_stage


@pytest.mark.parametrize("row", load_surface_provenance_inventory(), ids=lambda row: row.id)
def test_surface_provenance_inventory_t2_make_nodes_are_real_make_surfaces(
    row: SurfaceInventoryRow,
) -> None:
    make_nodes = [node.name for node in row.to_chain().nodes if node.kind == "make"]

    for name in make_nodes:
        assert name == "make" or name.startswith("make")


def test_surface_provenance_inventory_t2_verification_nodes_resolve_to_ssot_tests(
    inventory: tuple[SurfaceInventoryRow, ...],
) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    test_ids = {test["id"] for test in registry["tests"]}

    for row in inventory:
        verification_nodes = [
            node.name for node in row.to_chain().nodes if node.stage == "verification"
        ]
        assert verification_nodes
        assert set(verification_nodes) <= test_ids
