from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from ssot_authority_model import (  # noqa: E402
    derive_statuses,
    gate_report,
    load_registry,
    selection_manifest,
)


def _by_id(rows: list[dict], row_id: str) -> dict:
    return next(row for row in rows if row["id"] == row_id)


def test_boundary_selection_excludes_unscoped_feature_tests() -> None:
    manifest = selection_manifest(
        load_registry(), boundary_id="bnd:ssot-authority-migration-001"
    )

    assert "feat:ssot-authority-migration-001" in manifest["feature_ids"]
    assert "feat:canonical-op-create-001" not in manifest["feature_ids"]
    assert "tst:boundary-scoped-test-selection" in manifest["test_ids"]
    assert "tst:tigrbl-tests-tests-unit-test-core-crud-default-ops" not in manifest["test_ids"]


def test_status_sync_failed_test_cascades_to_evidence_and_claim() -> None:
    result = derive_statuses(
        load_registry(),
        {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "failed"}]},
    )

    assert result["tests"]["tst:status-sync-outcome-mapping"] == "failing"
    assert result["evidence"]["evd:ssot-status-sync-dry-run"] == "failed"
    assert result["claims"]["clm:status-sync-auditable-001"] == "blocked"


def test_gate_e_blocks_when_promotion_evidence_fails() -> None:
    registry = deepcopy(load_registry())
    target_evidence = next(
        evidence_id
        for claim in registry["claims"]
        if claim["id"] == "clm:gate-013"
        for evidence_id in claim["evidence_ids"]
    )
    for evidence in registry["evidence"]:
        if evidence["id"] == target_evidence:
            evidence["status"] = "failed"

    report = gate_report(registry)

    assert report["D"]["status"] == "passed"
    assert report["E"]["status"] == "blocked"
    assert target_evidence in report["E"]["non_passing_evidence_ids"]


def test_taxonomy_rows_keep_tools_tests_evidence_claims_and_gates_distinct() -> None:
    registry = load_registry()
    feature = _by_id(registry["features"], "feat:tool-test-gate-taxonomy-001")
    claim = _by_id(registry["claims"], "clm:tool-test-gate-taxonomy-001")

    assert feature["test_ids"] != feature["claim_ids"]
    assert "tst:tool-test-gate-taxonomy" in feature["test_ids"]
    assert claim["feature_ids"] == ["feat:tool-test-gate-taxonomy-001"]
    assert "tst:tool-test-gate-taxonomy" in claim["test_ids"]
    assert all(not test_id.startswith("clm:") for test_id in feature["test_ids"])

