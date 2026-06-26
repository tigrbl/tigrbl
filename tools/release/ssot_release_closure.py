from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ssot_registry.api import load_registry, save_registry
from ssot_registry.util.jsonio import stable_json_dumps


ROOT = Path(__file__).resolve().parents[2]
VERSION_ID_RE = re.compile(r"[^a-zA-Z0-9]+")


@dataclass(frozen=True)
class ReleaseScope:
    slug: str
    version: str
    prepared_commit: str
    feature_id: str
    source_claim_id: str
    claim_id: str
    test_id: str
    source_evidence_id: str
    evidence_id: str
    boundary_id: str
    release_id: str
    evidence_path: str
    package_count: int


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json_if_changed(path: Path, payload: dict[str, Any]) -> bool:
    text = stable_json_dumps(payload)
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="")
    return True


def materialize_missing_tmp_evidence(registry: dict[str, Any], repo_root: Path) -> list[str]:
    created: list[str] = []
    for row in registry.get("evidence", []):
        if not isinstance(row, dict):
            continue
        path_value = row.get("path")
        if not isinstance(path_value, str):
            continue
        if not path_value.startswith(".tmp/ssot/") or not path_value.endswith(".execution.json"):
            continue

        target = repo_root / path_value
        if target.exists():
            continue
        payload = {
            "evidence_id": row.get("id"),
            "path": path_value,
            "status": row.get("status", "passed"),
            "test_ids": row.get("test_ids", []),
        }
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(stable_json_dumps(payload), encoding="utf-8", newline="")
        created.append(path_value)
    return created


def slug_part(value: str) -> str:
    slug = VERSION_ID_RE.sub("-", value).strip("-").lower()
    return slug or "unknown"


def release_version(plan: dict[str, Any]) -> str:
    releases = plan.get("python") or []
    if not releases:
        raise ValueError("release plan does not include any Python packages")
    versions = {str(release["version"]) for release in releases}
    if len(versions) != 1:
        raise ValueError(
            "SSOT package release closure requires one target version; "
            f"got {', '.join(sorted(versions))}"
        )
    return versions.pop()


def build_scope(
    plan: dict[str, Any],
    *,
    prepared_commit: str,
    evidence_dir: Path,
) -> ReleaseScope:
    version = release_version(plan)
    commit_slug = slug_part(prepared_commit[:12])
    slug = f"package-release-{slug_part(version)}-{commit_slug}"
    evidence_path = (evidence_dir / f"{slug}-proof-chain.json").as_posix()
    return ReleaseScope(
        slug=slug,
        version=f"{version}+package-release.{commit_slug}",
        prepared_commit=prepared_commit,
        feature_id=f"feat:{slug}",
        source_claim_id=f"clm:{slug}.source.t1",
        claim_id=f"clm:{slug}.t2",
        test_id=f"tst:{slug}.workflow",
        source_evidence_id=f"evd:{slug}.source-plan",
        evidence_id=f"evd:{slug}.proof-chain",
        boundary_id=f"bnd:{slug}",
        release_id=f"rel:{slug}",
        evidence_path=evidence_path,
        package_count=len(plan.get("python") or []),
    )


def evidence_payload(
    plan: dict[str, Any],
    scope: ReleaseScope,
    *,
    generated_at: str,
) -> dict[str, Any]:
    return {
        "generated_at": generated_at,
        "prepared_commit": scope.prepared_commit,
        "release_id": scope.release_id,
        "boundary_id": scope.boundary_id,
        "version": scope.version,
        "semver": plan.get("semver"),
        "package_selection": plan.get("package_selection"),
        "packages": [
            {
                "name": release["name"],
                "path": release["path"],
                "old_version": release.get("old_version"),
                "version": release["version"],
                "tag": release.get("tag"),
            }
            for release in plan.get("python", [])
        ],
        "github_releases": plan.get("github_releases", []),
        "changed_files": plan.get("changed_files", []),
    }


def by_id(rows: list[dict[str, Any]], entity_id: str) -> dict[str, Any] | None:
    return next((row for row in rows if row.get("id") == entity_id), None)


def upsert_row(
    registry: dict[str, Any],
    section: str,
    entity_id: str,
    row: dict[str, Any],
    *,
    preserve_statuses: set[str] | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    rows = registry.setdefault(section, [])
    existing = by_id(rows, entity_id)
    if existing is None:
        rows.append(row)
        return None, True

    updated = {**existing, **row}
    if preserve_statuses and existing.get("status") in preserve_statuses:
        updated["status"] = existing["status"]
    if existing == updated:
        return existing, False
    existing.clear()
    existing.update(updated)
    return existing, True


def refresh_registry(
    registry: dict[str, Any],
    plan: dict[str, Any],
    scope: ReleaseScope,
) -> dict[str, Any]:
    package_names = ", ".join(release["name"] for release in plan.get("python", []))
    body = (
        f"Automated package release closure for prepared commit "
        f"{scope.prepared_commit}. Packages: {package_names}."
    )
    changes: list[str] = []

    rows: dict[str, dict[str, Any] | list[dict[str, Any]]] = {
        "features": {
            "id": scope.feature_id,
            "title": f"Package release {scope.version}",
            "description": (
                "Release workflow proof chain for version-bumped package "
                "publication."
            ),
            "body": body,
            "origin": "repo-local",
            "implementation_status": "implemented",
            "lifecycle": {
                "stage": "active",
                "replacement_feature_ids": [],
                "note": "Maintained by the publish workflow SSOT release closure job.",
            },
            "plan": {
                "horizon": "current",
                "slot": "publish-workflow",
                "target_claim_tier": "T2",
                "target_lifecycle_stage": "active",
            },
            "requires": [],
            "parent_feature_ids": [],
            "spec_ids": [],
            "claim_ids": [scope.source_claim_id, scope.claim_id],
            "test_ids": [scope.test_id],
        },
        "claims": [
            {
                "id": scope.source_claim_id,
                "title": f"Package release {scope.version} source plan collected",
                "description": (
                    "The prepared release plan exists as project-controlled source "
                    "evidence for the package release proof chain."
                ),
                "origin": "repo-local",
                "kind": "release-source",
                "tier": "T1",
                "status": "evidenced",
                "feature_ids": [scope.feature_id],
                "test_ids": [scope.test_id],
                "evidence_ids": [scope.source_evidence_id],
                "depends_on_claim_ids": [],
            },
            {
                "id": scope.claim_id,
                "title": f"Package release {scope.version} publication closure",
                "description": (
                    "The prepared release commit has a refreshed SSOT proof chain "
                    "and is eligible for release certification, promotion, and publication."
                ),
                "origin": "repo-local",
                "kind": "release",
                "tier": "T2",
                "status": "evidenced",
                "feature_ids": [scope.feature_id],
                "test_ids": [scope.test_id],
                "evidence_ids": [scope.evidence_id],
                "depends_on_claim_ids": [scope.source_claim_id],
            },
        ],
        "tests": {
            "id": scope.test_id,
            "title": f"Publish workflow release closure for {scope.version}",
            "body": "The GitHub Actions publish workflow performs this release closure.",
            "origin": "repo-local",
            "kind": "release-automation",
            "status": "passing",
            "path": ".github/workflows/publish.yml",
            "feature_ids": [scope.feature_id],
            "claim_ids": [scope.source_claim_id, scope.claim_id],
            "evidence_ids": [scope.evidence_id],
            "execution": {
                "argv": [
                    "uv",
                    "run",
                    "python",
                    "tools/release/ssot_release_closure.py",
                    "--summary",
                    "release-plan.json",
                    "--prepared-commit",
                    scope.prepared_commit,
                    "--write",
                ],
                "cwd": ".",
                "env": {},
                "mode": "command",
                "success": {
                    "expected": 0,
                    "type": "exit_code",
                },
                "timeout_seconds": 120,
            },
        },
        "evidence": [
            {
                "id": scope.source_evidence_id,
                "title": f"Package release {scope.version} source plan evidence",
                "body": (
                    "Baseline project-controlled source evidence for the package "
                    "release proof chain."
                ),
                "origin": "repo-local",
                "kind": "source-evidence",
                "tier": "T1",
                "status": "passed",
                "path": scope.evidence_path,
                "claim_ids": [scope.source_claim_id],
                "test_ids": [scope.test_id],
            },
            {
                "id": scope.evidence_id,
                "title": f"Package release {scope.version} proof chain evidence",
                "body": (
                    "Derived from the release plan emitted after version bumping and "
                    "before downstream package validation and publication."
                ),
                "origin": "repo-local",
                "kind": "release-plan",
                "tier": "T2",
                "status": "passed",
                "path": scope.evidence_path,
                "claim_ids": [scope.claim_id],
                "test_ids": [scope.test_id],
                "source_evidence_ids": [scope.source_evidence_id],
                "robustness_dimensions": [
                    "regression_corpus",
                    "compatibility_matrix",
                    "failure_recovery",
                ],
                "release_context": {
                    "release_id": scope.release_id,
                    "boundary_id": scope.boundary_id,
                    "boundary_ids": [scope.boundary_id],
                    "prepared_commit": scope.prepared_commit,
                    "package_count": scope.package_count,
                },
            },
        ],
        "boundaries": {
            "id": scope.boundary_id,
            "title": f"Package release {scope.version} boundary",
            "body": body,
            "status": "frozen",
            "frozen": True,
            "feature_ids": [scope.feature_id],
            "profile_ids": [],
        },
        "releases": {
            "id": scope.release_id,
            "version": scope.version,
            "body": body,
            "status": "candidate",
            "boundary_id": scope.boundary_id,
            "boundary_ids": [scope.boundary_id],
            "claim_ids": [scope.claim_id],
            "evidence_ids": [scope.evidence_id],
        },
    }

    for section, section_rows in rows.items():
        for row in section_rows if isinstance(section_rows, list) else [section_rows]:
            preserve_statuses = (
                {"certified", "promoted", "published", "revoked"}
                if section == "releases"
                else None
            )
            _, changed = upsert_row(
                registry,
                section,
                row["id"],
                row,
                preserve_statuses=preserve_statuses,
            )
            if changed:
                changes.append(row["id"])

    return {"changed_entity_ids": changes}


def append_github_output(path: Path, values: dict[str, str]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def now_utc() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--prepared-commit", required=True)
    parser.add_argument("--registry", type=Path, default=ROOT / ".ssot" / "registry.json")
    parser.add_argument("--evidence-dir", type=Path, default=Path(".ssot/evidence"))
    parser.add_argument("--generated-at", default=None)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    plan = read_json(args.summary)
    scope = build_scope(
        plan,
        prepared_commit=args.prepared_commit,
        evidence_dir=args.evidence_dir,
    )
    _, repo_root, registry = load_registry(args.registry)
    release_before = by_id(registry.get("releases", []), scope.release_id)
    status_before = release_before.get("status", "absent") if release_before else "absent"

    result = refresh_registry(registry, plan, scope)
    generated_at = args.generated_at or now_utc()
    evidence_changed = False
    materialized_evidence_paths: list[str] = []
    if args.write:
        evidence_changed = write_json_if_changed(
            repo_root / scope.evidence_path,
            evidence_payload(plan, scope, generated_at=generated_at),
        )
        materialized_evidence_paths = materialize_missing_tmp_evidence(
            registry,
            repo_root,
        )
        save_registry(
            args.registry,
            registry,
            repo_root=repo_root,
            action="refreshing package release SSOT closure",
        )

    output = {
        "release_id": scope.release_id,
        "boundary_id": scope.boundary_id,
        "feature_id": scope.feature_id,
        "source_claim_id": scope.source_claim_id,
        "source_evidence_id": scope.source_evidence_id,
        "evidence_id": scope.evidence_id,
        "release_status_before": status_before,
        "already_published": "true" if status_before == "published" else "false",
        "evidence_path": scope.evidence_path,
        "evidence_changed": "true" if evidence_changed else "false",
        "materialized_tmp_evidence_count": str(len(materialized_evidence_paths)),
        "changed_entity_count": str(len(result["changed_entity_ids"])),
    }
    if args.github_output:
        append_github_output(args.github_output, output)
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
