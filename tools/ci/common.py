from __future__ import annotations

from pathlib import Path
import sys


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def certification_projection_root() -> Path:
    return repo_root() / ".ssot" / "projections" / "certification"


def repo_relative(path: Path) -> str:
    return path.relative_to(repo_root()).as_posix()


def fail(errors: list[str]) -> None:
    if not errors:
        return
    print("VALIDATION FAILED", file=sys.stderr)
    for error in errors:
        print(f"- {error}", file=sys.stderr)
    raise SystemExit(1)
