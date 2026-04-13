from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()
MARKER_PATH = ROOT / "docs" / "conformance" / "gates" / "TARGET_FREEZE_CURRENT_CYCLE.json"


def git_changed_files(diff_range: str) -> set[str]:
    cmd = ["git", "diff", "--name-only", diff_range]
    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "git diff failed")
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def main() -> None:
    if not MARKER_PATH.is_file():
        fail([f"missing boundary freeze marker {MARKER_PATH.relative_to(ROOT)}"])

    completed = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        print("boundary freeze diff enforcement skipped: repository is not inside a git work tree")
        return

    marker = json.loads(MARKER_PATH.read_text())
    diff_range = os.environ.get("GATE_A_DIFF_RANGE", "").strip()
    if not diff_range:
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD~1"],
            cwd=ROOT,
            text=True,
            check=False,
            capture_output=True,
        )
        if probe.returncode != 0:
            print("boundary freeze diff enforcement skipped: no diff range available")
            return
        diff_range = "HEAD~1..HEAD"

    changed = git_changed_files(diff_range)
    errors: list[str] = []

    boundary_docs = set(marker.get("boundary_docs", []))
    controlled_docs = set(marker.get("controlled_docs", []))
    claim_registry = str(marker.get("claim_registry_path", "")).strip()
    manifest_path = str(marker.get("manifest_path", "")).strip()
    marker_path = str(MARKER_PATH.relative_to(ROOT))

    changed_boundary = boundary_docs & changed
    changed_controlled = controlled_docs & changed

    if changed_boundary and claim_registry not in changed:
        errors.append(
            "current-target boundary docs changed without a synchronized update to docs/conformance/CLAIM_REGISTRY.md"
        )

    if changed_controlled and manifest_path not in changed:
        errors.append(
            "freeze-controlled docs changed without an updated GATE_A_BOUNDARY_FREEZE_MANIFEST.json"
        )

    if manifest_path in changed and marker_path not in changed:
        errors.append(
            "the freeze manifest changed without a synchronized update to TARGET_FREEZE_CURRENT_CYCLE.json"
        )

    fail(errors)
    print("boundary freeze diff policy passed")


if __name__ == "__main__":
    main()
