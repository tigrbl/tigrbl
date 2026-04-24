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


def test_declared_surface_validator_passes() -> None:
    result = _run("tools/ci/validate_declared_surface.py")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_declared_surface_reports_and_ci_pointers_exist() -> None:
    current_state = (REPO_ROOT / ".ssot" / "reports" / "current_state" / "2026-04-07-phase1-declarative-surface.md").read_text(encoding="utf-8")
    cert_state = (REPO_ROOT / ".ssot" / "reports" / "certification_state" / "2026-04-07-phase1-declarative-surface.md").read_text(encoding="utf-8")
    ci_validation = (REPO_ROOT / "docs" / "developer" / "CI_VALIDATION.md").read_text(encoding="utf-8")
    assert "docs-surface metadata sourced from declared bindings rather than handwritten approximations" in current_state
    assert "active `0.3.19.dev1` remains a target/blocked line for certification purposes" in cert_state
    assert "validate_declared_surface.py" in ci_validation
