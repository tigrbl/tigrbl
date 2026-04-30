from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from whole_repo_certification_gap_report import build_report  # noqa: E402


def test_whole_repo_report_excludes_out_of_bounds_features() -> None:
    registry = {
        "features": [
            {
                "id": "feat:ready",
                "title": "Ready",
                "implementation_status": "implemented",
                "plan": {"horizon": "current"},
                "lifecycle": {"stage": "active"},
                "claim_ids": ["clm:ready"],
                "test_ids": ["tst:ready"],
            },
            {
                "id": "feat:oob",
                "title": "Out of bounds",
                "implementation_status": "absent",
                "plan": {"horizon": "out_of_bounds"},
                "lifecycle": {"stage": "active"},
                "claim_ids": [],
                "test_ids": [],
            },
        ],
        "claims": [{"id": "clm:ready", "status": "published", "evidence_ids": ["evd:ready"]}],
        "tests": [{"id": "tst:ready", "status": "passing", "evidence_ids": ["evd:ready"]}],
        "evidence": [{"id": "evd:ready", "status": "passed"}],
        "issues": [],
        "risks": [],
    }

    report = build_report(registry)

    assert report["candidate_boundary_feature_ids"] == ["feat:ready"]
    assert report["summary"]["feature_gap_count"] == 0


def test_whole_repo_report_flags_unimplemented_and_unproved_features() -> None:
    registry = {
        "features": [
            {
                "id": "feat:gap",
                "title": "Gap",
                "implementation_status": "partial",
                "plan": {"horizon": "current"},
                "lifecycle": {"stage": "active"},
                "claim_ids": ["clm:gap"],
                "test_ids": ["tst:gap"],
            }
        ],
        "claims": [{"id": "clm:gap", "status": "declared", "evidence_ids": ["evd:gap"]}],
        "tests": [{"id": "tst:gap", "status": "blocked", "evidence_ids": ["evd:gap"]}],
        "evidence": [{"id": "evd:gap", "status": "planned"}],
        "issues": [{"id": "iss:block", "title": "Block", "status": "open", "release_blocking": True}],
        "risks": [{"id": "rsk:block", "title": "Risk", "status": "active", "release_blocking": True}],
    }

    report = build_report(registry)
    row = report["feature_gaps"][0]

    assert row["id"] == "feat:gap"
    assert set(row["gaps"]) == {
        "feature_not_implemented",
        "non_passing_claims",
        "non_passing_evidence",
        "non_passing_tests",
    }
    assert report["summary"]["release_blocking_issue_count"] == 1
    assert report["summary"]["release_blocking_risk_count"] == 1
