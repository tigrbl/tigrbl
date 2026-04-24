from __future__ import annotations

import argparse
import json
from collections.abc import Iterable
from copy import deepcopy
from pathlib import Path
from typing import Any

from common import repo_root


ROOT = repo_root()
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"

GATE_CLAIMS: dict[str, tuple[str, ...]] = {
    "A": ("clm:gate-001", "clm:gate-002", "clm:gate-003", "clm:gate-004", "clm:gate-005", "clm:gate-006"),
    "B": ("clm:gate-007", "clm:gate-008"),
    "C": ("clm:gate-009", "clm:gate-010"),
    "D": ("clm:gate-011", "clm:gate-012"),
    "E": ("clm:gate-013", "clm:gate-014"),
}

PASSING_CLAIM_STATUSES = {"asserted", "accepted", "certified", "evidenced", "implemented", "passed", "verified"}
PASSING_EVIDENCE_STATUSES = {"passed", "accepted", "certified", "evidenced", "verified"}
RUNTIME_LANE_APPLICABILITY = {"required", "void", "not_applicable"}
RUNTIME_LANE_PATTERNS = (
    "runtime",
    "transport",
    "kernel",
    "canonical",
    "oltp",
    "sqlite",
    "postgres",
    "rest",
    "json-rpc",
    "jsonrpc",
    "websocket",
    "sse",
    "stream",
    "request envelope",
    "engine",
    "session",
    "transaction",
    "error",
    "performance",
    "parity",
    "docs/runtime",
    "status parity",
    "status projection",
)

OUTCOME_STATUS = {
    "pass": "passing",
    "passed": "passing",
    "success": "passing",
    "fail": "failing",
    "failed": "failing",
    "failure": "failing",
    "error": "failing",
    "errored": "failing",
    "skip": "blocked",
    "skipped": "blocked",
    "missing": "not_run",
    "not_run": "not_run",
}


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(registry: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in registry.get(key, [])}


def sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def linked_ids(registry: dict[str, Any], entity_key: str, link_field: str, target_key: str) -> list[str]:
    target_ids = set(by_id(registry, target_key))
    errors: list[str] = []
    for item in registry.get(entity_key, []):
        for linked_id in item.get(link_field, []):
            if linked_id not in target_ids:
                errors.append(f"{item['id']} links missing {link_field[:-4]} {linked_id}")
    return errors


def _runtime_lane_sensitive(feature: dict[str, Any]) -> bool:
    text = " ".join(str(feature.get(field, "")) for field in ("id", "title", "description")).lower()
    return any(pattern in text for pattern in RUNTIME_LANE_PATTERNS)


def _linked_rust_evidence(feature: dict[str, Any], tests: dict[str, dict[str, Any]], claims: dict[str, dict[str, Any]], evidence: dict[str, dict[str, Any]]) -> bool:
    def has_rust_text(item: dict[str, Any] | None) -> bool:
        if not item:
            return False
        text = " ".join(str(item.get(field, "")) for field in ("id", "title", "description", "path", "kind")).lower()
        return "rust" in text

    if feature["id"].startswith("feat:rust-"):
        return True
    if any(has_rust_text(claims.get(claim_id)) for claim_id in feature.get("claim_ids", [])):
        return True
    if any(has_rust_text(tests.get(test_id)) for test_id in feature.get("test_ids", [])):
        return True
    evidence_ids = {
        evidence_id
        for claim_id in feature.get("claim_ids", [])
        for evidence_id in claims.get(claim_id, {}).get("evidence_ids", [])
    }
    evidence_ids.update(
        evidence_id
        for test_id in feature.get("test_ids", [])
        for evidence_id in tests.get(test_id, {}).get("evidence_ids", [])
    )
    return any(has_rust_text(evidence.get(evidence_id)) for evidence_id in evidence_ids)


def validate_runtime_lanes(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    features = by_id(registry, "features")
    tests = by_id(registry, "tests")
    claims = by_id(registry, "claims")
    evidence = by_id(registry, "evidence")

    for feature in features.values():
        if not _runtime_lane_sensitive(feature):
            continue

        lanes = feature.get("runtime_lanes")
        if not isinstance(lanes, dict):
            errors.append(f"{feature['id']} is runtime-sensitive but has no runtime_lanes metadata")
            continue
        for lane in ("python", "rust"):
            lane_data = lanes.get(lane)
            if not isinstance(lane_data, dict):
                errors.append(f"{feature['id']} missing runtime_lanes.{lane}")
                continue
            applicability = lane_data.get("applicability")
            if applicability not in RUNTIME_LANE_APPLICABILITY:
                errors.append(f"{feature['id']} has invalid runtime_lanes.{lane}.applicability {applicability!r}")
                continue
            if applicability in {"void", "not_applicable"} and not str(lane_data.get("reason", "")).strip():
                errors.append(f"{feature['id']} runtime_lanes.{lane} {applicability} must include a reason")

        rust_lane = lanes.get("rust", {})
        if rust_lane.get("applicability") != "required":
            continue
        pair_ids = rust_lane.get("paired_feature_ids", [])
        if not isinstance(pair_ids, list):
            errors.append(f"{feature['id']} runtime_lanes.rust.paired_feature_ids must be a list")
            pair_ids = []
        missing_pairs = [pair_id for pair_id in pair_ids if pair_id not in features]
        for pair_id in missing_pairs:
            errors.append(f"{feature['id']} runtime_lanes.rust links missing paired feature {pair_id}")
        if pair_ids or _linked_rust_evidence(feature, tests, claims, evidence):
            continue
        errors.append(f"{feature['id']} requires Rust parity but has no Rust pair, claim, test, or evidence")
    return errors


def validate_authority_model(registry: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    adrs = by_id(registry, "adrs")
    specs = by_id(registry, "specs")
    features = by_id(registry, "features")
    tests = by_id(registry, "tests")
    claims = by_id(registry, "claims")
    evidence = by_id(registry, "evidence")

    for required in ("adr:1060", "adr:1082"):
        if required not in adrs:
            errors.append(f"missing authority ADR {required}")
    for required in ("spc:1002", "spc:2084", "spc:2085"):
        if required not in specs:
            errors.append(f"missing authority SPEC {required}")

    for feature in features.values():
        if not feature.get("test_ids"):
            errors.append(f"{feature['id']} has no linked tests or governance validator")
        for test_id in feature.get("test_ids", []):
            if test_id not in tests:
                errors.append(f"{feature['id']} links missing test {test_id}")
        for claim_id in feature.get("claim_ids", []):
            if claim_id not in claims:
                errors.append(f"{feature['id']} links missing claim {claim_id}")
        for spec_id in feature.get("spec_ids", []):
            if spec_id not in specs:
                errors.append(f"{feature['id']} links missing SPEC {spec_id}")

    errors.extend(linked_ids(registry, "claims", "feature_ids", "features"))
    errors.extend(linked_ids(registry, "claims", "test_ids", "tests"))
    errors.extend(linked_ids(registry, "claims", "evidence_ids", "evidence"))
    errors.extend(linked_ids(registry, "tests", "feature_ids", "features"))
    errors.extend(linked_ids(registry, "tests", "claim_ids", "claims"))
    errors.extend(linked_ids(registry, "tests", "evidence_ids", "evidence"))
    errors.extend(linked_ids(registry, "evidence", "claim_ids", "claims"))
    errors.extend(linked_ids(registry, "evidence", "test_ids", "tests"))
    errors.extend(validate_runtime_lanes(registry))

    for path in ("docs/conformance/GATE_MODEL.md", "docs/developer/CI_VALIDATION.md"):
        text = (ROOT / path).read_text(encoding="utf-8")
        if ".ssot/registry.json" not in text:
            errors.append(f"{path} does not point to SSOT registry authority")
        if "non-authoritative" not in text.lower():
            errors.append(f"{path} does not describe docs/CI as non-authoritative projection")

    return errors


def selection_manifest(registry: dict[str, Any], *, boundary_id: str | None = None, release_id: str | None = None) -> dict[str, Any]:
    boundaries = by_id(registry, "boundaries")
    releases = by_id(registry, "releases")
    features = by_id(registry, "features")
    claims = by_id(registry, "claims")
    tests = by_id(registry, "tests")

    if release_id:
        release = releases[release_id]
        boundary_id = release["boundary_id"]
        release_claims = release.get("claim_ids", [])
        release_evidence = release.get("evidence_ids", [])
    else:
        release_claims = []
        release_evidence = []
    if not boundary_id:
        raise ValueError("boundary_id or release_id is required")

    boundary = boundaries[boundary_id]
    feature_ids = sorted_unique(boundary.get("feature_ids", []))
    claim_ids = sorted_unique(
        list(release_claims)
        + [claim_id for feature_id in feature_ids for claim_id in features[feature_id].get("claim_ids", [])]
    )
    test_ids = sorted_unique(
        [test_id for feature_id in feature_ids for test_id in features[feature_id].get("test_ids", [])]
        + [test_id for claim_id in claim_ids for test_id in claims.get(claim_id, {}).get("test_ids", [])]
    )
    evidence_ids = sorted_unique(
        list(release_evidence)
        + [evidence_id for claim_id in claim_ids for evidence_id in claims.get(claim_id, {}).get("evidence_ids", [])]
        + [evidence_id for test_id in test_ids for evidence_id in tests.get(test_id, {}).get("evidence_ids", [])]
    )
    return {
        "boundary_id": boundary_id,
        "release_id": release_id,
        "feature_ids": feature_ids,
        "claim_ids": claim_ids,
        "test_ids": test_ids,
        "evidence_ids": evidence_ids,
    }


def derive_statuses(registry: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    derived = {
        "tests": {},
        "evidence": {},
        "claims": {},
        "gates": {},
    }
    test_results = {
        item["id"]: OUTCOME_STATUS.get(str(item.get("outcome", "")).lower(), "not_run")
        for item in results.get("tests", [])
    }
    tests = by_id(registry, "tests")
    evidence = by_id(registry, "evidence")
    claims = by_id(registry, "claims")

    for test_id in tests:
        derived["tests"][test_id] = test_results.get(test_id, "not_run")

    for evidence_id, item in evidence.items():
        statuses = [derived["tests"].get(test_id, "not_run") for test_id in item.get("test_ids", [])]
        if not statuses:
            derived["evidence"][evidence_id] = item.get("status", "not_run")
        elif any(status == "failing" for status in statuses):
            derived["evidence"][evidence_id] = "failed"
        elif any(status == "blocked" for status in statuses):
            derived["evidence"][evidence_id] = "blocked"
        elif any(status == "not_run" for status in statuses):
            derived["evidence"][evidence_id] = "not_run"
        else:
            derived["evidence"][evidence_id] = "passed"

    for claim_id, item in claims.items():
        evidence_statuses = [derived["evidence"].get(evidence_id, "not_run") for evidence_id in item.get("evidence_ids", [])]
        if evidence_statuses and all(status in PASSING_EVIDENCE_STATUSES for status in evidence_statuses):
            derived["claims"][claim_id] = "asserted"
        elif any(status == "failed" for status in evidence_statuses):
            derived["claims"][claim_id] = "blocked"
        elif any(status in {"blocked", "not_run"} for status in evidence_statuses):
            derived["claims"][claim_id] = "declared"
        else:
            derived["claims"][claim_id] = item.get("status", "declared")

    prior_passed = True
    for gate, claim_ids in GATE_CLAIMS.items():
        statuses = [derived["claims"].get(claim_id, claims.get(claim_id, {}).get("status", "declared")) for claim_id in claim_ids]
        passed = prior_passed and all(status in PASSING_CLAIM_STATUSES for status in statuses)
        derived["gates"][gate] = "passed" if passed else "blocked"
        prior_passed = passed
    return derived


def gate_report(registry: dict[str, Any]) -> dict[str, Any]:
    claims = by_id(registry, "claims")
    evidence = by_id(registry, "evidence")
    report: dict[str, Any] = {}
    prior_passed = True
    for gate, claim_ids in GATE_CLAIMS.items():
        missing = [claim_id for claim_id in claim_ids if claim_id not in claims]
        bad_claims = [
            claim_id for claim_id in claim_ids
            if claim_id in claims and claims[claim_id].get("status") not in PASSING_CLAIM_STATUSES
        ]
        bad_evidence = [
            evidence_id
            for claim_id in claim_ids
            for evidence_id in claims.get(claim_id, {}).get("evidence_ids", [])
            if evidence.get(evidence_id, {}).get("status") not in PASSING_EVIDENCE_STATUSES
        ]
        passed = prior_passed and not missing and not bad_claims and not bad_evidence
        report[gate] = {
            "status": "passed" if passed else "blocked",
            "claim_ids": list(claim_ids),
            "missing_claim_ids": missing,
            "non_passing_claim_ids": bad_claims,
            "non_passing_evidence_ids": sorted_unique(bad_evidence),
        }
        prior_passed = passed
    return report


def apply_status_dry_run(registry: dict[str, Any], results: dict[str, Any]) -> dict[str, Any]:
    derived = derive_statuses(registry, results)
    planned = deepcopy(registry)
    tests = by_id(planned, "tests")
    for test_id, status in derived["tests"].items():
        if test_id in tests:
            tests[test_id]["status"] = status
    return {"mode": "dry-run", "derived": derived, "registry": planned}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boundary-id")
    parser.add_argument("--release-id")
    parser.add_argument("--results")
    parser.add_argument("--mode", choices=("select", "gates", "sync"), required=True)
    args = parser.parse_args()
    registry = load_registry()
    if args.mode == "select":
        payload = selection_manifest(registry, boundary_id=args.boundary_id, release_id=args.release_id)
    elif args.mode == "gates":
        payload = gate_report(registry)
    else:
        results = json.loads(Path(args.results).read_text(encoding="utf-8")) if args.results else {"tests": []}
        if isinstance(results, dict) and isinstance(results.get("input"), dict):
            results = results["input"]
        payload = apply_status_dry_run(registry, results)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
