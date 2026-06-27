import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_runtime_boundary_validator_passes():
    result = subprocess.run(
        [sys.executable, "tools/ci/validate_runtime_boundary.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
