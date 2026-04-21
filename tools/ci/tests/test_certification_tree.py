from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "tools" / "ci"))

from simple_yaml import load_yaml

BOUNDARY = REPO_ROOT / "certification" / "boundary.yaml"
NEXT_TARGET = REPO_ROOT / "certification" / "targets" / "next_target.yaml"
CLAIM_FILES = [
    REPO_ROOT / "certification" / "claims" / "current.yaml",
    REPO_ROOT / "certification" / "claims" / "target.yaml",
    REPO_ROOT / "certification" / "claims" / "blocked.yaml",
    REPO_ROOT / "certification" / "claims" / "evidenced.yaml",
]
CURRENT_STATE_REPORT = REPO_ROOT / "reports" / "current_state" / "2026-04-07-phase0-certification-freeze.md"
CERTIFICATION_STATE_REPORT = REPO_ROOT / "reports" / "certification_state" / "2026-04-07-registry-reclassification.md"


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, script],
        cwd=REPO_ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )


def _load_yaml(path: Path) -> object:
    return load_yaml(path.read_text(encoding="utf-8"))


def test_certification_tree_validator_passes() -> None:
    result = _run("tools/ci/validate_certification_tree.py")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_boundary_truth_model_uses_four_explicit_states() -> None:
    boundary = _load_yaml(BOUNDARY)
    assert isinstance(boundary, dict)
    truth_model = boundary["authority"]["truth_model"]
    states = {state["id"] for state in truth_model["states"]}
    assert states == {"current", "target", "blocked", "evidenced"}


def test_public_claims_define_certified_boundary_flag() -> None:
    for path in CLAIM_FILES:
        payload = _load_yaml(path)
        assert isinstance(payload, dict)
        for claim in payload["claims"]:
            if claim["public"]:
                assert "certified_boundary" in claim, (path, claim["id"])


def test_next_target_phase0_exit_criteria_are_fully_declared() -> None:
    payload = _load_yaml(NEXT_TARGET)
    assert isinstance(payload, dict)
    target_claim_ids = {
        claim["id"]
        for claim in _load_yaml(REPO_ROOT / "certification" / "claims" / "target.yaml")["claims"]
    }
    for feature in payload["features"]:
        for field in ("owner", "package", "crate", "test_class", "claim_target", "evidence_artifacts"):
            assert feature[field]
        assert feature["claim_target"] in target_claim_ids
        for artifact in feature["evidence_artifacts"]:
            assert (REPO_ROOT / artifact).exists()
    for risk in payload["risks"]:
        assert risk["mitigation_owner"]
    for issue in payload["issues"]:
        assert issue.get("phase_link") or issue.get("waiver")


def test_blocked_claims_are_lifecycle_tracked() -> None:
    lifecycle = _load_yaml(REPO_ROOT / "certification" / "claims" / "lifecycle.yaml")
    blocked = _load_yaml(REPO_ROOT / "certification" / "claims" / "blocked.yaml")
    lifecycle_ids = {claim["id"] for claim in lifecycle["claims"]}
    for claim in blocked["claims"]:
        assert claim["id"] in lifecycle_ids


def test_phase0_reports_record_machine_validated_checkpoint() -> None:
    current_state = CURRENT_STATE_REPORT.read_text(encoding="utf-8")
    certification_state = CERTIFICATION_STATE_REPORT.read_text(encoding="utf-8")
    assert "certification-tree validator" in current_state
    assert "machine-validated" in certification_state
