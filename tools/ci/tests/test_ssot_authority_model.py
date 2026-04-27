from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from ssot_authority_model import (  # noqa: E402
    apply_status_dry_run,
    derive_statuses,
    gate_report,
    load_registry,
    selection_manifest,
    validate_authority_model,
    validate_runtime_lanes,
)


def test_repo_ssot_authority_model_validates() -> None:
    assert validate_authority_model(load_registry()) == []


def test_feature_without_test_or_governance_rationale_fails() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-missing-verification",
            "title": "Fixture missing verification",
            "description": "Negative fixture.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": [],
            "test_ids": [],
            "requires": [],
            "spec_ids": ["spc:2084"],
        }
    )
    errors = validate_authority_model(registry)
    assert "feat:fixture-missing-verification has no linked tests or governance validator" in errors


def test_governance_only_feature_with_validator_passes() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-governance-only",
            "title": "Fixture governance only",
            "description": "Positive fixture covered by governance validator.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": ["clm:ssot-authority-projection-001"],
            "test_ids": ["tst:ssot-authority-model-validator"],
            "requires": [],
            "spec_ids": ["spc:2084"],
        }
    )
    assert validate_authority_model(registry) == []


def test_runtime_sensitive_feature_without_rust_lane_fails() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-runtime-without-rust-lane",
            "title": "Fixture runtime without Rust lane",
            "description": "Negative fixture for runtime governance.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": ["clm:ssot-authority-projection-001"],
            "test_ids": ["tst:ssot-authority-model-validator"],
            "requires": [],
            "spec_ids": ["spc:2090"],
        }
    )
    errors = validate_runtime_lanes(registry)
    assert "feat:fixture-runtime-without-rust-lane is runtime-sensitive but has no runtime_lanes metadata" in errors


def test_future_absent_runtime_feature_does_not_require_runtime_lanes() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-future-runtime-planning-row",
            "title": "Fixture future runtime planning row",
            "description": "Planning-only runtime row.",
            "implementation_status": "absent",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "future", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": [],
            "test_ids": [],
            "requires": [],
            "spec_ids": ["spc:2090"],
        }
    )
    assert validate_runtime_lanes(registry) == []


def test_obsolete_out_of_bounds_alias_does_not_require_verification() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-obsolete-alias",
            "title": "Fixture obsolete alias",
            "description": "Compatibility row for a replaced feature.",
            "implementation_status": "partial",
            "lifecycle": {
                "stage": "obsolete",
                "replacement_feature_ids": ["feat:fixture-governance-only"],
                "note": "Replaced by explicit feature ID feat:fixture-governance-only.",
            },
            "plan": {
                "horizon": "out_of_bounds",
                "slot": "legacy-feature-id-alias",
                "target_claim_tier": None,
                "target_lifecycle_stage": "obsolete",
            },
            "claim_ids": [],
            "test_ids": [],
            "requires": [],
            "spec_ids": [],
        }
    )
    assert validate_authority_model(registry) == []


def test_backlog_partial_runtime_feature_does_not_require_runtime_lanes() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-backlog-partial-runtime",
            "title": "Fixture backlog partial runtime row",
            "description": "Backlog runtime row with partial implementation evidence elsewhere.",
            "implementation_status": "partial",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "backlog", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": [],
            "test_ids": [],
            "requires": [],
            "spec_ids": ["spc:2090"],
        }
    )
    assert validate_runtime_lanes(registry) == []


def test_void_or_not_applicable_runtime_lane_requires_reason() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-runtime-void-without-reason",
            "title": "Fixture runtime void without reason",
            "description": "Negative fixture for runtime governance.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": ["clm:ssot-authority-projection-001"],
            "test_ids": ["tst:ssot-authority-model-validator"],
            "requires": [],
            "spec_ids": ["spc:2090"],
            "runtime_lanes": {
                "python": {"applicability": "required"},
                "rust": {"applicability": "not_applicable"},
            },
        }
    )
    errors = validate_runtime_lanes(registry)
    assert "feat:fixture-runtime-void-without-reason runtime_lanes.rust not_applicable must include a reason" in errors


def test_required_rust_lane_requires_rust_evidence_or_pair() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-runtime-required-without-rust-evidence",
            "title": "Fixture runtime required without Rust evidence",
            "description": "Negative fixture for runtime governance.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": ["clm:ssot-authority-projection-001"],
            "test_ids": ["tst:ssot-authority-model-validator"],
            "requires": [],
            "spec_ids": ["spc:2090"],
            "runtime_lanes": {
                "python": {"applicability": "required"},
                "rust": {"applicability": "required"},
            },
        }
    )
    errors = validate_runtime_lanes(registry)
    assert "feat:fixture-runtime-required-without-rust-evidence requires Rust parity but has no Rust pair, claim, test, or evidence" in errors


def test_required_rust_lane_accepts_explicit_pair() -> None:
    registry = deepcopy(load_registry())
    registry["features"].append(
        {
            "id": "feat:fixture-runtime-required-with-pair",
            "title": "Fixture runtime required with pair",
            "description": "Positive fixture for runtime governance.",
            "implementation_status": "implemented",
            "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
            "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
            "claim_ids": ["clm:ssot-authority-projection-001"],
            "test_ids": ["tst:ssot-authority-model-validator"],
            "requires": [],
            "spec_ids": ["spc:2090"],
            "runtime_lanes": {
                "python": {"applicability": "required"},
                "rust": {
                    "applicability": "required",
                    "paired_feature_ids": ["feat:rust-runtime-ddl-initialization-boundary-001"],
                },
            },
        }
    )
    assert validate_runtime_lanes(registry) == []


def test_boundary_selection_is_deterministic() -> None:
    registry = load_registry()
    left = selection_manifest(registry, boundary_id="bnd:ssot-authority-migration-001")
    right = selection_manifest(registry, boundary_id="bnd:ssot-authority-migration-001")
    assert left == right
    assert left["feature_ids"] == sorted(left["feature_ids"])
    assert "tst:ssot-authority-model-validator" in left["test_ids"]
    assert "evd:ssot-boundary-test-selection" in left["evidence_ids"]


def test_release_selection_resolves_boundary() -> None:
    registry = load_registry()
    manifest = selection_manifest(registry, release_id="rel:0.3.19.dev1-ssot-authority-migration")
    assert manifest["boundary_id"] == "bnd:ssot-authority-migration-001"
    assert "clm:boundary-test-selection-deterministic-001" in manifest["claim_ids"]


@pytest.mark.parametrize(
    ("outcome", "expected"),
    [
        ("passed", "passing"),
        ("failed", "failing"),
        ("error", "failing"),
        ("skipped", "blocked"),
        ("missing", "not_run"),
    ],
)
def test_status_sync_maps_test_outcomes(outcome: str, expected: str) -> None:
    registry = load_registry()
    derived = derive_statuses(registry, {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": outcome}]})
    assert derived["tests"]["tst:status-sync-outcome-mapping"] == expected


def test_status_sync_dry_run_does_not_mutate_input() -> None:
    registry = load_registry()
    before = deepcopy(registry)
    result = apply_status_dry_run(registry, {"tests": [{"id": "tst:status-sync-outcome-mapping", "outcome": "failed"}]})
    assert registry == before
    assert result["mode"] == "dry-run"
    assert result["registry"] != registry


def test_gate_evaluator_aggregates_claims_and_prior_gates() -> None:
    report = gate_report(load_registry())
    assert list(report) == ["A", "B", "C", "D", "E"]
    assert report["B"]["claim_ids"] == ["clm:gate-007", "clm:gate-008"]
    assert report["E"]["claim_ids"] == ["clm:gate-013", "clm:gate-014"]


def test_gate_b_blocks_when_surface_claim_is_open() -> None:
    registry = deepcopy(load_registry())
    for claim in registry["claims"]:
        if claim["id"] == "clm:gate-007":
            claim["status"] = "declared"
    report = gate_report(registry)
    assert report["B"]["status"] == "blocked"
    assert report["C"]["status"] == "blocked"


def test_gate_c_blocks_when_conformance_claim_is_open() -> None:
    registry = deepcopy(load_registry())
    for claim in registry["claims"]:
        if claim["id"] == "clm:gate-009":
            claim["status"] = "declared"
    report = gate_report(registry)
    assert report["B"]["status"] == "passed"
    assert report["C"]["status"] == "blocked"


def test_gate_d_blocks_when_reproducibility_evidence_fails() -> None:
    registry = deepcopy(load_registry())
    target_evidence = next(
        evidence_id
        for claim in registry["claims"]
        if claim["id"] == "clm:gate-011"
        for evidence_id in claim["evidence_ids"]
    )
    for evidence in registry["evidence"]:
        if evidence["id"] == target_evidence:
            evidence["status"] = "failed"
    report = gate_report(registry)
    assert report["D"]["status"] == "blocked"
    assert report["E"]["status"] == "blocked"


def test_docs_and_ci_projection_drift_is_detected() -> None:
    registry = load_registry()
    assert validate_authority_model(registry) == []
    gate_model = (REPO_ROOT / "docs" / "conformance" / "GATE_MODEL.md").read_text(encoding="utf-8")
    assert ".ssot/registry.json" in gate_model
    assert "non-authoritative" in gate_model.lower()
