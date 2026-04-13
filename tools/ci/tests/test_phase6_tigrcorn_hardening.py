from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


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


def test_phase6_tigrcorn_hardening_validator_passes() -> None:
    result = _run("tools/ci/validate_phase6_tigrcorn_hardening.py")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_phase6_reports_and_cli_surface_exist() -> None:
    current_state = (REPO_ROOT / "reports" / "current_state" / "2026-04-09-phase6-tigrcorn-hardening.md").read_text(encoding="utf-8")
    cert_state = (REPO_ROOT / "reports" / "certification_state" / "2026-04-09-phase6-tigrcorn-hardening.md").read_text(encoding="utf-8")
    cli_reference = (REPO_ROOT / "docs" / "developer" / "CLI_REFERENCE.md").read_text(encoding="utf-8")
    assert "five blessed deployment profiles" in current_state
    assert "Profile claims remain blocked until profile-specific negative corpora and mixed-topology lanes are executed as governed release evidence" in cert_state
    assert "--deployment-profile" in cli_reference
