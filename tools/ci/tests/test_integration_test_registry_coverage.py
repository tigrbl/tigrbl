from __future__ import annotations

import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO / ".ssot" / "registry.json"
I9N_ROOT = REPO / "pkgs" / "core" / "tigrbl_tests" / "tests" / "i9n"
FEATURE_ID = "feat:integration-test-registry-coverage-001"


def _load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _i9n_paths() -> set[str]:
    return {
        path.relative_to(REPO).as_posix()
        for path in sorted(I9N_ROOT.glob("test_*.py"))
    }


def test_every_integration_test_file_has_registry_row_and_existing_path() -> None:
    registry = _load_registry()
    tests = registry["tests"]
    rows_by_path = {
        row.get("path"): row
        for row in tests
        if isinstance(row.get("path"), str)
        and row["path"].startswith("pkgs/97_tests/tigrbl_tests/tests/i9n/")
    }

    missing = sorted(_i9n_paths() - set(rows_by_path))
    stale = sorted(path for path in rows_by_path if not (REPO / path).exists())

    assert missing == []
    assert stale == []


def test_integration_registry_coverage_feature_has_reciprocal_test_links() -> None:
    registry = _load_registry()
    feature = next(row for row in registry["features"] if row["id"] == FEATURE_ID)
    feature_test_ids = set(feature.get("test_ids", ()))
    i9n_rows = [
        row
        for row in registry["tests"]
        if isinstance(row.get("path"), str)
        and row["path"].startswith("pkgs/97_tests/tigrbl_tests/tests/i9n/")
    ]

    unlinked_from_feature = sorted(
        row["id"] for row in i9n_rows if row["id"] not in feature_test_ids
    )
    missing_feature_backlink = sorted(
        row["id"] for row in i9n_rows if FEATURE_ID not in set(row.get("feature_ids", ()))
    )

    assert unlinked_from_feature == []
    assert missing_feature_backlink == []


def test_integration_registry_coverage_claim_has_t2_proof_links() -> None:
    registry = _load_registry()
    feature = next(row for row in registry["features"] if row["id"] == FEATURE_ID)
    claims = {
        row["id"]: row
        for row in registry["claims"]
        if FEATURE_ID in set(row.get("feature_ids", ()))
    }
    evidence = {row["id"]: row for row in registry["evidence"]}

    t2_claims = [row for row in claims.values() if row.get("tier") == "T2"]

    assert feature["implementation_status"] == "implemented"
    assert feature["plan"]["target_claim_tier"] == "T2"
    assert t2_claims
    for claim in t2_claims:
        assert claim.get("test_ids")
        assert claim.get("evidence_ids")
        assert all(evidence[eid]["status"] == "passed" for eid in claim["evidence_ids"])
