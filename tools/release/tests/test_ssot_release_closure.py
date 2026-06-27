from __future__ import annotations

from pathlib import Path

from tools.release.ssot_release_closure import (
    build_scope,
    materialize_missing_tmp_evidence,
    refresh_registry,
    release_version,
    write_json_if_changed,
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
        scope.source_claim_id,
        scope.claim_id,
        scope.test_id,
        scope.source_evidence_id,
        scope.evidence_id,
        scope.boundary_id,
        scope.release_id,
    ]
    release = registry["releases"][0]  # type: ignore[index]
    assert release["status"] == "candidate"
    assert release["boundary_id"] == scope.boundary_id
    assert release["claim_ids"] == [scope.claim_id]
    assert release["evidence_ids"] == [scope.evidence_id]
    source_claim, claim = registry["claims"]  # type: ignore[misc]
    assert source_claim["id"] == scope.source_claim_id
    assert source_claim["tier"] == "T1"
    assert source_claim["evidence_ids"] == [scope.source_evidence_id]
    assert claim["evidence_ids"] == [scope.evidence_id]
    assert claim["depends_on_claim_ids"] == [scope.source_claim_id]
    source_evidence, proof_evidence = registry["evidence"]  # type: ignore[misc]
    assert source_evidence["id"] == scope.source_evidence_id
    assert source_evidence["tier"] == "T1"
    assert source_evidence["status"] == "passed"
    assert source_evidence["claim_ids"] == [scope.source_claim_id]
    assert proof_evidence["id"] == scope.evidence_id
    assert proof_evidence["tier"] == "T2"
    assert proof_evidence["status"] == "passed"
    assert proof_evidence["source_evidence_ids"] == [scope.source_evidence_id]
    assert "regression_corpus" in proof_evidence["robustness_dimensions"]


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


def test_release_version_uses_span_for_mixed_package_versions() -> None:
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

    assert release_version(plan) == "0.4.4.dev2-to-0.4.4.dev3"


def test_release_scope_uses_span_for_mixed_package_versions() -> None:
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

    scope = build_scope(
        plan,
        prepared_commit="ab4923ed1d278ea87b44f63c1896d74a6affbc4a",
        evidence_dir=Path("ignored"),
    )

    assert (
        scope.release_id
        == "rel:package-release-0-4-4-dev2-to-0-4-4-dev3-ab4923ed1d27"
    )
    assert scope.version == "0.4.4.dev2-to-0.4.4.dev3+package-release.ab4923ed1d27"


def test_write_json_if_changed_uses_canonical_compact_json(tmp_path: Path) -> None:
    target = tmp_path / "evidence.json"

    changed = write_json_if_changed(target, {"z": 1, "a": {"b": 2}})

    assert changed is True
    assert target.read_text(encoding="utf-8") == '{"a":{"b":2},"z":1}'


def test_materialize_missing_tmp_evidence_creates_ignored_execution_artifact(
    tmp_path: Path,
) -> None:
    registry: dict[str, object] = {
        "evidence": [
            {
                "id": "evd:transport-proof",
                "path": ".tmp/ssot/transport-proof.execution.json",
                "status": "passed",
                "test_ids": ["tst:transport-proof"],
            },
            {
                "id": "evd:committed-proof",
                "path": ".ssot/evidence/committed-proof.json",
                "status": "passed",
            },
        ],
    }

    created = materialize_missing_tmp_evidence(registry, tmp_path)

    assert created == [".tmp/ssot/transport-proof.execution.json"]
    assert (
        tmp_path / ".tmp" / "ssot" / "transport-proof.execution.json"
    ).read_text(encoding="utf-8") == (
        '{"evidence_id":"evd:transport-proof","path":'
        '".tmp/ssot/transport-proof.execution.json","status":"passed",'
        '"test_ids":["tst:transport-proof"]}'
    )


def test_materialize_missing_tmp_evidence_leaves_existing_artifact(
    tmp_path: Path,
) -> None:
    target = tmp_path / ".tmp" / "ssot" / "transport-proof.execution.json"
    target.parent.mkdir(parents=True)
    target.write_text('{"existing":true}', encoding="utf-8")
    registry: dict[str, object] = {
        "evidence": [
            {
                "id": "evd:transport-proof",
                "path": ".tmp/ssot/transport-proof.execution.json",
            },
        ],
    }

    assert materialize_missing_tmp_evidence(registry, tmp_path) == []
    assert target.read_text(encoding="utf-8") == '{"existing":true}'
