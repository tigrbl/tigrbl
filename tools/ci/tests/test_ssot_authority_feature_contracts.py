from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from ssot_authority_model import load_registry, selection_manifest  # noqa: E402


def _by_id(rows: list[dict], row_id: str) -> dict:
    return next(row for row in rows if row["id"] == row_id)


def test_ssot_authority_features_share_projection_claim_and_specs() -> None:
    registry = load_registry()
    features = registry["features"]

    authority = _by_id(features, "feat:ssot-authority-migration-001")
    projection = _by_id(features, "feat:docs-ci-projection-validation-001")

    for feature in (authority, projection):
        assert "clm:ssot-authority-projection-001" in feature["claim_ids"]
        assert {"spc:1002", "spc:2084", "spc:2085"} <= set(feature["spec_ids"])
        assert {
            "tst:ssot-authority-model-validator",
            "tst:docs-ci-projection-drift",
        } <= set(feature["test_ids"])


def test_docs_ci_projection_selection_includes_authority_drift_tests() -> None:
    manifest = selection_manifest(
        load_registry(), boundary_id="bnd:ssot-authority-migration-001"
    )

    assert "feat:ssot-authority-migration-001" in manifest["feature_ids"]
    assert "feat:docs-ci-projection-validation-001" in manifest["feature_ids"]
    assert "tst:ssot-authority-model-validator" in manifest["test_ids"]
    assert "tst:docs-ci-projection-drift" in manifest["test_ids"]

