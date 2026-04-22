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


def test_rust_parity_validator_passes() -> None:
    result = _run("tools/ci/validate_rust_parity.py")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_rust_parity_reports_and_ci_pointers_exist() -> None:
    current_state = (REPO_ROOT / ".ssot" / "reports" / "current_state" / "2026-04-09-phase4-native-parity.md").read_text(encoding="utf-8")
    cert_state = (REPO_ROOT / ".ssot" / "reports" / "certification_state" / "2026-04-09-phase4-native-parity.md").read_text(encoding="utf-8")
    ci_validation = (REPO_ROOT / "docs" / "developer" / "CI_VALIDATION.md").read_text(encoding="utf-8")
    assert "differential Python-vs-native parity suites" in current_state
    assert "native backend claims remain blocked until the parity lanes are both implemented and passed as release evidence" in cert_state
    assert "validate_rust_parity.py" in ci_validation
