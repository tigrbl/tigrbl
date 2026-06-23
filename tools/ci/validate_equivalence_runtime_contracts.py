from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

from common import fail, repo_root


ROOT = repo_root()
PROJECT = ROOT / "examples" / "equivalence_contracts"


def _workspace_pythonpath() -> str:
    paths = [PROJECT / "src", ROOT]
    for base in (ROOT / "pkgs" / "core", ROOT / "pkgs" / "apps", ROOT / "pkgs" / "engines"):
        if not base.is_dir():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir():
                continue
            paths.append(child)
            src = child / "src"
            if src.is_dir():
                paths.append(src)
    return os.pathsep.join(str(path) for path in paths)


def main() -> None:
    errors: list[str] = []
    if not (PROJECT / "pyproject.toml").is_file():
        errors.append("examples/equivalence_contracts/pyproject.toml is missing")
    if not (PROJECT / "src" / "tigrbl_equivalence_contracts").is_dir():
        errors.append("examples/equivalence_contracts runtime package is missing")
    if errors:
        fail(errors)

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = _workspace_pythonpath()
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            "examples/equivalence_contracts/tests",
        ],
        cwd=ROOT,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(
            [
                "equivalence runtime contract tests failed\n"
                f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            ]
        )
    print("equivalence runtime contract validation passed")


if __name__ == "__main__":
    main()
