from __future__ import annotations

from pathlib import Path

import pytest

from tools.release.ssot_release_closure import (
    build_scope,
    refresh_registry,
    release_version,
)


def _plan(version: str = "0.4.4.dev2") -> dict[str, object]:
    return {
        "semver": "patch",
        "package_selection": "all",
        "changed_files": ["pkgs/tigrbl/pyproject.toml"],
        "python": [
            {
                "name": "tigrbl",
                "path": "pkgs/tigrbl/pyproject.toml",
                "old_version": "0.4.4.dev1",
                "version": version,
                "tag": f"tigrbl=={version}",
            }
        ],
        "github_releases": [
            {
                "name": "tigrbl",
                "path": "pkgs/tigrbl/pyproject.toml",
                "old_version": "0.4.4.dev1",
                "version": version,
                "tag": f"tigrbl=={version}",
            }
        ],
    }


def test_release_scope_uses_version_and_prepared_commit() -> None:
    scope = build_scope(
        _plan(),
        prepared_commit="ab4923ed1d278ea87b44f63c1896d74a6affbc4a",
        evidence_dir=Path("ignored"),
    )

    assert scope.release_id == "rel:package-release-0-4-4-dev2-ab4923ed1d27"
    assert scope.boundary_id == "bnd:package-release-0-4-4-dev2-ab4923ed1d27"
    assert scope.version == "0.4.4.dev2+package-release.ab4923ed1d27"


def test_refresh_registry_creates_linked_release_proof_rows() -> None:
    registry: dict[str, object] = {
        "features": [],
        "claims": [],
        "tests": [],
        "evidence": [],
        "boundaries": [],
        "releases": [],
    }
    scope = build_scope(
        _plan(),
        prepared_commit="ab4923ed1d278ea87b44f63c1896d74a6affbc4a",
        evidence_dir=Path("ignored"),
    )

    result = refresh_registry(registry, _plan(), scope)

    assert result["changed_entity_ids"] == [
        scope.feature_id,
        scope.claim_id,
        scope.test_id,
        scope.evidence_id,
        scope.boundary_id,
        scope.release_id,
    ]
    release = registry["releases"][0]  # type: ignore[index]
    assert release["status"] == "candidate"
    assert release["boundary_id"] == scope.boundary_id
    assert release["claim_ids"] == [scope.claim_id]
    assert release["evidence_ids"] == [scope.evidence_id]


def test_refresh_registry_preserves_published_release_status() -> None:
    scope = build_scope(
        _plan(),
        prepared_commit="ab4923ed1d278ea87b44f63c1896d74a6affbc4a",
        evidence_dir=Path("ignored"),
    )
    registry: dict[str, object] = {
        "features": [],
        "claims": [],
        "tests": [],
        "evidence": [],
        "boundaries": [],
        "releases": [{"id": scope.release_id, "status": "published"}],
    }

    refresh_registry(registry, _plan(), scope)

    assert registry["releases"][0]["status"] == "published"  # type: ignore[index]


def test_release_version_rejects_mixed_package_versions() -> None:
    plan = _plan()
    plan["python"].append(  # type: ignore[index, union-attr]
        {
            "name": "tigrbl-core",
            "path": "pkgs/core/tigrbl_core/pyproject.toml",
            "old_version": "0.4.4.dev1",
            "version": "0.4.4.dev3",
            "tag": "tigrbl-core==0.4.4.dev3",
        }
    )

    with pytest.raises(ValueError, match="one target version"):
        release_version(plan)
