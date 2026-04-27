from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from ssot_authority_model import (  # noqa: E402
    apply_status_dry_run,
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


def test_boundary_selection_is_stable_and_sorted() -> None:
    first = selection_manifest(
        load_registry(), boundary_id="bnd:ssot-authority-migration-001"
    )
    second = selection_manifest(
        load_registry(), boundary_id="bnd:ssot-authority-migration-001"
    )

    assert first == second
    assert first["feature_ids"] == sorted(first["feature_ids"])
    assert first["claim_ids"] == sorted(first["claim_ids"])
    assert first["test_ids"] == sorted(first["test_ids"])
    assert first["evidence_ids"] == sorted(first["evidence_ids"])


def test_release_selection_includes_release_evidence_and_boundary_features() -> None:
    registry = load_registry()
    release = registry["releases"][0]
    manifest = selection_manifest(registry, release_id=release["id"])

    assert manifest["release_id"] == release["id"]
    assert manifest["boundary_id"] == release["boundary_id"]
    assert set(release.get("claim_ids", [])).issubset(manifest["claim_ids"])
    assert set(release.get("evidence_ids", [])).issubset(manifest["evidence_ids"])


def test_boundary_selection_rejects_unknown_boundary() -> None:
    try:
        selection_manifest(load_registry(), boundary_id="bnd:missing-boundary")
    except KeyError as exc:
        assert "bnd:missing-boundary" in str(exc)
    else:
        raise AssertionError("unknown boundary selection must fail closed")


def test_feature_coverage_completeness_target_rows_have_claims_and_tests() -> None:
    registry = load_registry()
    targets = [
        "feat:boundary-scoped-test-selection-001",
        "feat:feature-test-coverage-completeness-001",
        "feat:gate-evaluator-model-001",
        "feat:test-result-evidence-ingestion-001",
        "feat:tool-test-gate-taxonomy-001",
        "feat:status-sync-engine-001",
    ]

    for feature_id in targets:
        feature = _by_id(registry["features"], feature_id)
        assert feature["implementation_status"] == "implemented"
        assert feature["claim_ids"], feature_id
        assert feature["test_ids"], feature_id


def test_status_sync_failed_test_cascades_to_evidence_and_claim() -> None:
    result = derive_statuses(
        load_registry(),
        {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "failed"}]},
    )

    assert result["tests"]["tst:status-sync-outcome-mapping"] == "failing"
    assert result["evidence"]["evd:ssot-status-sync-dry-run"] == "failed"
    assert result["claims"]["clm:status-sync-auditable-001"] == "blocked"


def test_status_sync_skipped_test_blocks_evidence_without_certifying_claim() -> None:
    result = derive_statuses(
        load_registry(),
        {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "skipped"}]},
    )

    assert result["tests"]["tst:status-sync-outcome-mapping"] == "blocked"
    assert result["evidence"]["evd:ssot-status-sync-dry-run"] == "blocked"
    assert result["claims"]["clm:status-sync-auditable-001"] == "declared"


def test_status_sync_dry_run_preserves_source_registry() -> None:
    registry = load_registry()
    original_test = _by_id(registry["tests"], "tst:status-sync-outcome-mapping")
    original_status = original_test["status"]

    result = apply_status_dry_run(
        registry,
        {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "failed"}]},
    )

    assert result["mode"] == "dry-run"
    assert result["registry"] is not registry
    assert _by_id(registry["tests"], "tst:status-sync-outcome-mapping")["status"] == original_status
    assert _by_id(result["registry"]["tests"], "tst:status-sync-outcome-mapping")["status"] == "failing"


def test_status_sync_unknown_outcome_is_not_run() -> None:
    result = derive_statuses(
        load_registry(),
        {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "unexpected"}]},
    )

    assert result["tests"]["tst:status-sync-outcome-mapping"] == "not_run"
    assert result["evidence"]["evd:ssot-status-sync-dry-run"] == "not_run"


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


def test_gate_report_explains_missing_and_non_passing_claims() -> None:
    registry = deepcopy(load_registry())
    gate_a_claim = _by_id(registry["claims"], "clm:gate-001")
    gate_a_claim["status"] = "declared"
    registry["claims"] = [
        claim for claim in registry["claims"] if claim["id"] != "clm:gate-002"
    ]

    report = gate_report(registry)

    assert report["A"]["status"] == "blocked"
    assert "clm:gate-001" in report["A"]["non_passing_claim_ids"]
    assert "clm:gate-002" in report["A"]["missing_claim_ids"]
    assert report["B"]["status"] == "blocked"


def test_taxonomy_rows_keep_tools_tests_evidence_claims_and_gates_distinct() -> None:
    registry = load_registry()
    feature = _by_id(registry["features"], "feat:tool-test-gate-taxonomy-001")
    claim = _by_id(registry["claims"], "clm:tool-test-gate-taxonomy-001")

    assert feature["test_ids"] != feature["claim_ids"]
    assert "tst:tool-test-gate-taxonomy" in feature["test_ids"]
    assert claim["feature_ids"] == ["feat:tool-test-gate-taxonomy-001"]
    assert "tst:tool-test-gate-taxonomy" in claim["test_ids"]
    assert all(not test_id.startswith("clm:") for test_id in feature["test_ids"])


def test_taxonomy_claim_requires_evidence_not_only_tool_or_test_link() -> None:
    registry = deepcopy(load_registry())
    claim = _by_id(registry["claims"], "clm:tool-test-gate-taxonomy-001")
    claim["evidence_ids"] = []

    result = derive_statuses(registry, {"tests": [{"id": "tst:tool-test-gate-taxonomy", "outcome": "passed"}]})

    assert result["tests"]["tst:tool-test-gate-taxonomy"] == "passing"
    assert result["claims"]["clm:tool-test-gate-taxonomy-001"] == claim["status"]
