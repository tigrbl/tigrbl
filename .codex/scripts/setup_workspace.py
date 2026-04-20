from __future__ import annotations

import os
import subprocess
from pathlib import Path


def run(command: list[str], *, env: dict[str, str]) -> None:
    subprocess.run(command, check=True, env=env)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["UV_CACHE_DIR"] = str(root / ".uv-cache")

    venv_path = root / ".tmp" / "codex-venv"
    run(
        [
            "uv",
            "venv",
            str(venv_path),
            "--allow-existing",
            "--python",
            "3.12",
            "--python-preference",
            "only-system",
        ],
        env=env,
    )

    env["VIRTUAL_ENV"] = str(venv_path.resolve())
    env["PATH"] = str(venv_path / "Scripts") + os.pathsep + env.get("PATH", "")

    run(["cargo", "fetch", "--locked"], env=env)
    run(
        [
            "uv",
            "sync",
            "--active",
            "--all-packages",
            "--all-groups",
            "--all-extras",
            "--python-preference",
            "only-system",
        ],
        env=env,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
