from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]


def _workflow(name: str) -> str:
    return (REPO_ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")


def test_gate_d_workflow_invokes_smokes_validator_and_tests_without_bypass() -> None:
    workflow = _workflow("gate-d-reproducibility.yml")

    assert "tools/conformance/clean_room_package_smoke.py" in workflow
    assert "tools/conformance/installed_package_smoke.py" in workflow
    assert "tools/ci/validate_gate_d_reproducibility.py" in workflow
    assert "tools/ci/tests/test_gate_d_reproducibility.py" in workflow
    assert "continue-on-error" not in workflow


def test_post_promotion_handoff_workflow_fails_if_validation_and_repair_fail() -> None:
    workflow = _workflow("post-promotion-handoff.yml")

    assert "tools/ci/validate_post_promotion_handoff.py" in workflow
    assert "tools/ci/fix_post_promotion_handoff.py" in workflow
    assert "tools/ci/tests/test_post_promotion_handoff.py" in workflow
    assert "Fail when handoff validation stays broken" in workflow
    assert "exit 1" in workflow
    assert (
        "steps.validate-post-promotion-handoff.outcome == 'failure' "
        "&& steps.revalidate-post-promotion-handoff.outcome == 'failure'"
    ) in workflow


def test_post_promotion_handoff_workflow_runs_tigrbl_tests_after_successful_validation() -> None:
    workflow = _workflow("post-promotion-handoff.yml")

    assert "pkgs/core/tigrbl_tests/tests" in workflow
    assert "steps.validate-post-promotion-handoff.outcome == 'success'" in workflow
    assert "steps.revalidate-post-promotion-handoff.outcome == 'success'" in workflow
