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


def test_claim_lifecycle_validator_passes() -> None:
    result = _run("tools/ci/validate_claim_lifecycle.py")
    assert result.returncode == 0, f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"


def test_claim_lifecycle_bundle_and_reports_exist() -> None:
    current_state = (REPO_ROOT / ".ssot" / "reports" / "current_state" / "2026-04-09-phase7-claims-evidence-promotion.md").read_text(encoding="utf-8")
    cert_state = (REPO_ROOT / ".ssot" / "reports" / "certification_state" / "2026-04-09-phase7-claims-evidence-promotion.md").read_text(encoding="utf-8")
    bundle = REPO_ROOT / "docs" / "conformance" / "releases" / "0.3.18" / "artifacts" / "certification-bundle.json"
    assert "claim lifecycle registry" in current_state
    assert "active `0.3.19.dev1` remains non-certifiable" in cert_state
    assert bundle.exists()
