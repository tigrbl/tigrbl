from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from common import repo_root


ROOT = repo_root()
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"
DEFAULT_JSON_REPORT = ROOT / ".ssot" / "reports" / "whole-repo-certification-gaps.json"
DEFAULT_MD_REPORT = ROOT / ".ssot" / "reports" / "whole-repo-certification-gaps.md"

PASSING_CLAIM_STATUSES = {
    "accepted",
    "asserted",
    "certified",
    "evidenced",
    "implemented",
    "passed",
    "published",
    "verified",
}
PASSING_TEST_STATUSES = {"passed", "passing", "verified"}
PASSING_EVIDENCE_STATUSES = {
    "accepted",
    "certified",
    "evidenced",
    "passed",
    "verified",
}
PASSING_ISSUE_STATUSES = {"closed", "resolved", "done"}
PASSING_RISK_STATUSES = {"accepted", "closed", "mitigated", "retired"}


def _load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {row["id"]: row for row in rows}


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _is_out_of_scope(feature: dict[str, Any]) -> bool:
    horizon = str(feature.get("plan", {}).get("horizon", "") or "").lower()
    lifecycle_stage = str(feature.get("lifecycle", {}).get("stage", "") or "").lower()
    return horizon == "out_of_bounds" or lifecycle_stage in {"obsolete", "removed"}


def _feature_gaps(
    feature: dict[str, Any],
    claims: dict[str, dict[str, Any]],
    tests: dict[str, dict[str, Any]],
    evidence: dict[str, dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    if feature.get("implementation_status") != "implemented":
        gaps.append("feature_not_implemented")
    claim_ids = list(feature.get("claim_ids", []))
    test_ids = list(feature.get("test_ids", []))
    if not claim_ids:
        gaps.append("missing_claims")
    if not test_ids:
        gaps.append("missing_tests")

    non_passing_claims = [
        claim_id
        for claim_id in claim_ids
        if claims.get(claim_id, {}).get("status") not in PASSING_CLAIM_STATUSES
    ]
    non_passing_tests = [
        test_id
        for test_id in test_ids
        if tests.get(test_id, {}).get("status") not in PASSING_TEST_STATUSES
    ]

    linked_evidence_ids = _sorted_unique(
        [
            evidence_id
            for claim_id in claim_ids
            for evidence_id in claims.get(claim_id, {}).get("evidence_ids", [])
        ]
        + [
            evidence_id
            for test_id in test_ids
            for evidence_id in tests.get(test_id, {}).get("evidence_ids", [])
        ]
    )
    if not linked_evidence_ids:
        gaps.append("missing_evidence")
    non_passing_evidence = [
        evidence_id
        for evidence_id in linked_evidence_ids
        if evidence.get(evidence_id, {}).get("status") not in PASSING_EVIDENCE_STATUSES
    ]

    if non_passing_claims:
        gaps.append("non_passing_claims")
    if non_passing_tests:
        gaps.append("non_passing_tests")
    if non_passing_evidence:
        gaps.append("non_passing_evidence")
    return gaps


def build_report(registry: dict[str, Any]) -> dict[str, Any]:
    features = registry.get("features", [])
    claims = _by_id(registry.get("claims", []))
    tests = _by_id(registry.get("tests", []))
    evidence = _by_id(registry.get("evidence", []))

    in_bound_features = [feature for feature in features if not _is_out_of_scope(feature)]
    out_of_scope_features = [feature for feature in features if _is_out_of_scope(feature)]
    feature_gap_rows: list[dict[str, Any]] = []
    for feature in in_bound_features:
        gaps = _feature_gaps(feature, claims, tests, evidence)
        if gaps:
            feature_gap_rows.append(
                {
                    "id": feature["id"],
                    "title": feature.get("title"),
                    "implementation_status": feature.get("implementation_status"),
                    "horizon": feature.get("plan", {}).get("horizon"),
                    "slot": feature.get("plan", {}).get("slot"),
                    "gaps": gaps,
                    "claim_ids": feature.get("claim_ids", []),
                    "test_ids": feature.get("test_ids", []),
                }
            )

    release_blocking_issues = [
        {
            "id": issue["id"],
            "title": issue.get("title"),
            "status": issue.get("status"),
        }
        for issue in registry.get("issues", [])
        if issue.get("release_blocking") is True
        and str(issue.get("status", "")).lower() not in PASSING_ISSUE_STATUSES
    ]
    release_blocking_risks = [
        {
            "id": risk["id"],
            "title": risk.get("title"),
            "status": risk.get("status"),
        }
        for risk in registry.get("risks", [])
        if risk.get("release_blocking") is True
        and str(risk.get("status", "")).lower() not in PASSING_RISK_STATUSES
    ]

    gap_counts = Counter(gap for row in feature_gap_rows for gap in row["gaps"])
    implementation_counts = Counter(
        str(feature.get("implementation_status", "unknown")) for feature in in_bound_features
    )
    horizon_counts = Counter(
        str(feature.get("plan", {}).get("horizon", "unknown")) for feature in features
    )

    return {
        "target": {
            "boundary_id": "bnd:tigrbl-whole-repo-certification-001",
            "release_id": "rel:tigrbl-0.4.0",
            "scope": "all SSOT features except out_of_bounds, obsolete, and removed rows",
        },
        "summary": {
            "total_features": len(features),
            "in_bound_features": len(in_bound_features),
            "out_of_scope_features": len(out_of_scope_features),
            "feature_gap_count": len(feature_gap_rows),
            "gap_counts": dict(sorted(gap_counts.items())),
            "implementation_counts": dict(sorted(implementation_counts.items())),
            "horizon_counts": dict(sorted(horizon_counts.items())),
            "release_blocking_issue_count": len(release_blocking_issues),
            "release_blocking_risk_count": len(release_blocking_risks),
        },
        "candidate_boundary_feature_ids": sorted(feature["id"] for feature in in_bound_features),
        "feature_gaps": sorted(feature_gap_rows, key=lambda row: row["id"]),
        "release_blocking_issues": release_blocking_issues,
        "release_blocking_risks": release_blocking_risks,
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Whole-Repo Certification Gap Report",
        "",
        "This report is generated from `.ssot/registry.json` and defines the fail-closed gap set for `rel:tigrbl-0.4.0`.",
        "",
        "## Summary",
        "",
    ]
    for key, value in report["summary"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Release Blockers",
            "",
            "| Type | ID | Status | Title |",
            "|---|---|---|---|",
        ]
    )
    blockers = report["release_blocking_issues"] + report["release_blocking_risks"]
    if blockers:
        for blocker in report["release_blocking_issues"]:
            lines.append(f"| issue | `{blocker['id']}` | `{blocker.get('status')}` | {blocker.get('title')} |")
        for blocker in report["release_blocking_risks"]:
            lines.append(f"| risk | `{blocker['id']}` | `{blocker.get('status')}` | {blocker.get('title')} |")
    else:
        lines.append("| none |  |  |  |")

    lines.extend(
        [
            "",
            "## Feature Gaps",
            "",
            "| Feature | Status | Horizon | Gaps |",
            "|---|---|---|---|",
        ]
    )
    for row in report["feature_gaps"]:
        gaps = ", ".join(f"`{gap}`" for gap in row["gaps"])
        lines.append(
            f"| `{row['id']}` | `{row.get('implementation_status')}` | `{row.get('horizon')}` | {gaps} |"
        )
    return "\n".join(lines) + "\n"


def write_reports(
    report: dict[str, Any],
    *,
    json_path: Path = DEFAULT_JSON_REPORT,
    markdown_path: Path = DEFAULT_MD_REPORT,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(_markdown(report), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_REPORT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MD_REPORT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report(_load_registry())
    if args.check:
        print(json.dumps(report["summary"], indent=2, sort_keys=True))
        if report["feature_gaps"] or report["release_blocking_issues"] or report["release_blocking_risks"]:
            raise SystemExit(1)
        return
    write_reports(report, json_path=args.json_output, markdown_path=args.markdown_output)
    print(json.dumps(report["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
