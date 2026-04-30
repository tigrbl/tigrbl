from __future__ import annotations

import json
from pathlib import Path

try:
    import tomllib
except ImportError:  # pragma: no cover
    import tomli as tomllib


REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / ".ssot" / "registry.json"
REPORT_PATH = REPO_ROOT / ".ssot" / "reports" / "package-coordinate-traceability-plan-2026-04-28.md"

PASSING_CLAIM_STATUSES = {"asserted", "certified", "evidenced", "published", "verified"}
PASSING_EVIDENCE_STATUSES = {"passed", "certified", "evidenced", "published", "verified"}
PASSING_TEST_STATUSES = {"passing", "passed", "verified"}


def _project_names() -> set[str]:
    names: set[str] = set()
    for pyproject in (REPO_ROOT / "pkgs").rglob("pyproject.toml"):
        if "archive" in pyproject.parts:
            continue
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        name = data.get("project", {}).get("name")
        if isinstance(name, str) and name:
            names.add(name.replace("_", "-"))
    return names


def _registry_feature_text() -> str:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return "\n".join(
        " ".join(
            str(feature.get(key, ""))
            for key in ("id", "title", "description")
        )
        for feature in registry.get("features", [])
    ).replace("_", "-")


def _registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def test_package_coordinate_traceability_is_closed() -> None:
    feature_text = _registry_feature_text()
    missing = {
        name
        for name in _project_names()
        if name not in feature_text
    }

    assert not missing

    report = REPORT_PATH.read_text(encoding="utf-8")
    for name in sorted(_project_names()):
        assert f"`{name}`" in report


def test_package_proof_chain_release_blocker_is_resolved() -> None:
    registry = _registry()
    features = _by_id(registry["features"])
    claims = _by_id(registry["claims"])
    tests = _by_id(registry["tests"])
    evidence = _by_id(registry["evidence"])
    issues = _by_id(registry["issues"])
    risks = _by_id(registry["risks"])

    feature_ids = [
        "feat:package-buildability-importability-001",
        "feat:package-coordinate-traceability-closure-001",
    ]
    claim_ids = [
        "clm:pkg-buildability-importability-001",
        "clm:package-coordinate-traceability-closure-001",
    ]
    test_ids = [
        "tst:tools-ci-tests-test_packages_buildable_importable.py",
        "tst:package-coordinate-traceability-gap-current",
    ]
    evidence_ids = [
        "evd:pkg-buildability-importability-001",
        "evd:package-coordinate-traceability-plan-20260428",
    ]

    assert all(features[feature_id]["implementation_status"] == "implemented" for feature_id in feature_ids)
    assert all(claims[claim_id]["status"] in PASSING_CLAIM_STATUSES for claim_id in claim_ids)
    assert all(tests[test_id]["status"] in PASSING_TEST_STATUSES for test_id in test_ids)
    assert all(evidence[evidence_id]["status"] in PASSING_EVIDENCE_STATUSES for evidence_id in evidence_ids)
    assert issues["iss:certifiable-package-proof-chain-gap-001"]["status"] == "closed"
    assert issues["iss:certifiable-package-proof-chain-gap-001"]["release_blocking"] is False
    assert risks["rsk:unverified-package-proof-chain-001"]["status"] == "mitigated"
