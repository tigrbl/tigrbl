from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "conformance"))

from build_full_feature_certification_target import (  # noqa: E402
    BOUNDARY_ID,
    REPORT_PATH,
    feature_row,
    is_excluded,
)


def load_registry() -> dict:
    return json.loads((REPO_ROOT / ".ssot" / "registry.json").read_text(encoding="utf-8"))


def active_gap_rows(registry: dict) -> list[dict]:
    return [
        feature_row(feature)
        for feature in sorted(registry["features"], key=lambda item: item["id"])
        if feature.get("implementation_status") in {"absent", "partial"} and not is_excluded(feature)
    ]


def test_full_feature_certification_boundary_matches_active_gap_set() -> None:
    registry = load_registry()
    expected_ids = [row["id"] for row in active_gap_rows(registry)]
    boundary = next(item for item in registry["boundaries"] if item["id"] == BOUNDARY_ID)

    assert boundary["status"] == "draft"
    assert boundary["frozen"] is False
    assert boundary["feature_ids"] == expected_ids


def test_full_feature_certification_report_matches_registry_boundary() -> None:
    registry = load_registry()
    rows = active_gap_rows(registry)
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

    assert report["boundary_id"] == BOUNDARY_ID
    assert report["boundary_status"] == "draft"
    assert report["summary"]["total_active_gaps"] == len(rows)
    assert report["summary"]["absent"] == sum(1 for row in rows if row["implementation_status"] == "absent")
    assert report["summary"]["partial"] == sum(1 for row in rows if row["implementation_status"] == "partial")
    assert report["features"] == rows


def test_exclusion_policy_keeps_disposition_rows_out_of_full_implementation_target() -> None:
    base = {
        "id": "feat:fixture",
        "title": "Fixture",
        "description": "Fixture",
        "implementation_status": "partial",
        "lifecycle": {"stage": "active", "replacement_feature_ids": [], "note": None},
        "plan": {"horizon": "current", "slot": None, "target_claim_tier": "T2", "target_lifecycle_stage": "active"},
        "claim_ids": [],
        "test_ids": [],
    }
    assert not is_excluded(base)
    assert is_excluded({**base, "plan": {**base["plan"], "horizon": "out_of_bounds"}})
    assert is_excluded({**base, "lifecycle": {**base["lifecycle"], "stage": "deprecated"}})
    assert is_excluded({**base, "title": "Obsolete alias for old feature"})
    assert is_excluded({**base, "description": "Surface is descoped from certification"})
