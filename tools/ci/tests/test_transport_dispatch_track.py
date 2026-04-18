from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def _run(script: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run([sys.executable, script], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)


def test_transport_dispatch_track_validator_passes() -> None:
    result = _run("tools/ci/validate_transport_dispatch_track.py")
    assert result.returncode == 0, f"STDOUT\n{result.stdout}\nSTDERR\n{result.stderr}"
