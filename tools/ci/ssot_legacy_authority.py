from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

from common import repo_root

ROOT = repo_root()
REGISTRY_PATH = ROOT / ".ssot" / "registry.json"

LEGACY_CLAIM_ID_RE = re.compile(r"^(?:[A-Z]+-\d+|RFC-\d+|OIDC-\d+)$")
LEGACY_SSOT_CLAIM_RE = re.compile(
    r"^clm:(?:gov|path|gate|evid|cert|oas|rpc|op|cli|sec|rfc|oidc|handoff|next)-\d+$"
)
PASSING_CLAIM_STATUSES = {
    "asserted",
    "accepted",
    "certified",
    "evidenced",
    "implemented",
    "passed",
    "published",
    "verified",
}
PASSING_EVIDENCE_STATUSES = {
    "accepted",
    "certified",
    "evidenced",
    "passed",
    "published",
    "verified",
}


@dataclass(frozen=True)
class ClaimRow:
    display_id: str
    ssot_id: str
    title: str
    status: str
    tier: str
    claim: dict[str, Any]


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def by_id(registry: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {
        str(row["id"]): row
        for row in registry.get(key, [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def ssot_to_display_id(ssot_id: str) -> str:
    if not ssot_id.startswith("clm:"):
        raise ValueError(f"{ssot_id!r} is not an SSOT claim id")
    return ssot_id.removeprefix("clm:").upper()


def display_to_ssot_id(display_id: str) -> str:
    return f"clm:{display_id.lower()}"


def legacy_claim_rows(registry: dict[str, Any] | None = None) -> dict[str, ClaimRow]:
    registry = registry or load_registry()
    rows: dict[str, ClaimRow] = {}
    for claim in registry.get("claims", []):
        if not isinstance(claim, dict):
            continue
        ssot_id = str(claim.get("id", ""))
        if not LEGACY_SSOT_CLAIM_RE.fullmatch(ssot_id):
            continue
        display_id = ssot_to_display_id(ssot_id)
        if not LEGACY_CLAIM_ID_RE.fullmatch(display_id):
            continue
        rows[display_id] = ClaimRow(
            display_id=display_id,
            ssot_id=ssot_id,
            title=str(claim.get("title", "")),
            status=str(claim.get("status", "")).lower(),
            tier=str(claim.get("tier", "")),
            claim=claim,
        )
    return rows


def is_claim_passing(row: ClaimRow | dict[str, Any]) -> bool:
    status = row.status if isinstance(row, ClaimRow) else str(row.get("status", "")).lower()
    return status in PASSING_CLAIM_STATUSES


def require_claim_rows(display_ids: Iterable[str], rows: dict[str, ClaimRow] | None = None) -> list[str]:
    available = rows or legacy_claim_rows()
    return sorted(set(display_ids) - set(available))


def path_spec_exists(spec: str) -> bool:
    path_part = spec.split("::", 1)[0].split("#", 1)[0].strip()
    return bool(path_part) and (ROOT / path_part).exists()


def linked_evidence(row: ClaimRow, registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = registry or load_registry()
    evidence = by_id(registry, "evidence")
    return [evidence[evidence_id] for evidence_id in row.claim.get("evidence_ids", []) if evidence_id in evidence]


def linked_tests(row: ClaimRow, registry: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    registry = registry or load_registry()
    tests = by_id(registry, "tests")
    return [tests[test_id] for test_id in row.claim.get("test_ids", []) if test_id in tests]


def validate_claim_links(
    display_ids: Iterable[str] | None = None,
    registry: dict[str, Any] | None = None,
) -> list[str]:
    registry = registry or load_registry()
    rows = legacy_claim_rows(registry)
    evidence_by_id = by_id(registry, "evidence")
    tests_by_id = by_id(registry, "tests")
    claim_ids = sorted(display_ids or rows)
    errors: list[str] = []

    for display_id in claim_ids:
        row = rows.get(display_id)
        if row is None:
            errors.append(f"missing SSOT claim row for {display_id} ({display_to_ssot_id(display_id)})")
            continue

        evidence_ids = [str(item) for item in row.claim.get("evidence_ids", [])]
        test_ids = [str(item) for item in row.claim.get("test_ids", [])]
        if not evidence_ids:
            errors.append(f"{display_id} has no linked SSOT evidence_ids")
        if not test_ids:
            errors.append(f"{display_id} has no linked SSOT test_ids")

        for evidence_id in evidence_ids:
            evidence = evidence_by_id.get(evidence_id)
            if evidence is None:
                errors.append(f"{display_id} links missing SSOT evidence {evidence_id}")
                continue
            status = str(evidence.get("status", "")).lower()
            if status not in PASSING_EVIDENCE_STATUSES:
                errors.append(f"{display_id} links non-passing evidence {evidence_id} ({status!r})")
            path = str(evidence.get("path", "")).strip()
            if path and not path_spec_exists(path):
                errors.append(f"{display_id} evidence {evidence_id} references missing path: {path}")

        for test_id in test_ids:
            test = tests_by_id.get(test_id)
            if test is None:
                errors.append(f"{display_id} links missing SSOT test {test_id}")
                continue
            path = str(test.get("path", "")).strip()
            if path and not path_spec_exists(path):
                errors.append(f"{display_id} test {test_id} references missing path: {path}")

    return errors


def assert_claims_passing(display_ids: Iterable[str], rows: dict[str, ClaimRow] | None = None) -> list[str]:
    available = rows or legacy_claim_rows()
    errors: list[str] = []
    for display_id in sorted(display_ids):
        row = available.get(display_id)
        if row is None:
            errors.append(f"missing SSOT claim row for {display_id} ({display_to_ssot_id(display_id)})")
        elif not is_claim_passing(row):
            errors.append(f"{display_id} must have a passing SSOT status (got {row.status!r})")
    return errors


def validate_active_boundary_frozen(
    registry: dict[str, Any] | None = None,
    *,
    expected_boundary_id: str | None = None,
) -> list[str]:
    registry = registry or load_registry()
    errors: list[str] = []
    active_boundary_id = str(registry.get("program", {}).get("active_boundary_id", "")).strip()
    if expected_boundary_id and active_boundary_id != expected_boundary_id:
        errors.append(f"active SSOT boundary must be {expected_boundary_id}")
    if not active_boundary_id:
        errors.append(".ssot/registry.json must define program.active_boundary_id")
        return errors

    boundary = by_id(registry, "boundaries").get(active_boundary_id)
    if boundary is None:
        errors.append(f"active SSOT boundary row is missing: {active_boundary_id}")
        return errors
    if boundary.get("status") != "frozen":
        errors.append(f"active SSOT boundary {active_boundary_id} must be frozen")
    if boundary.get("frozen") is not True:
        errors.append(f"active SSOT boundary {active_boundary_id} frozen flag must be true")
    return errors


def _sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(dict.fromkeys(value for value in values if value))


def _path_from_row(row: dict[str, Any]) -> str:
    return str(row.get("path", "")).strip()


def evidence_registry_projection(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    registry = registry or load_registry()
    rows = legacy_claim_rows(registry)
    fallback_registry_ref = ".ssot/registry.json"
    claims: dict[str, dict[str, list[str]]] = {}

    for display_id, row in sorted(rows.items()):
        evidence_rows = linked_evidence(row, registry)
        test_rows = linked_tests(row, registry)
        evidence_paths = [_path_from_row(item) for item in evidence_rows]
        test_paths = [_path_from_row(item) for item in test_rows]
        workflow_paths = [
            path for path in evidence_paths + test_paths if path.startswith(".github/workflows/")
        ]
        doc_paths = [
            path
            for path in evidence_paths
            if path.startswith("docs/") or path.startswith(".ssot/adr/") or path.startswith(".ssot/specs/")
        ]
        artifact_paths = [
            path
            for path in evidence_paths
            if path and path not in workflow_paths and path not in doc_paths
        ]

        fallback = f"{fallback_registry_ref}#{row.ssot_id}"
        claims[display_id] = {
            "lane_classes": _sorted_unique(
                [
                    str(row.claim.get("kind", "")).replace("_", " "),
                    *(str(item.get("kind", "")).replace("_", " ") for item in evidence_rows),
                    *(str(item.get("kind", "")).replace("_", " ") for item in test_rows),
                ]
            )
            or ["ssot-linkage"],
            "tests": _sorted_unique(test_paths) or [fallback],
            "ci_jobs": _sorted_unique(workflow_paths) or [fallback],
            "artifact_paths": _sorted_unique(artifact_paths) or [fallback],
            "doc_paths": _sorted_unique(doc_paths) or [fallback],
        }

    return {
        "schema_version": 1,
        "source": ".ssot/registry.json",
        "claims": claims,
    }
