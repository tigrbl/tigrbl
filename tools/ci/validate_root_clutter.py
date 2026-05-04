from __future__ import annotations

from pathlib import Path
import re
from common import repo_root, fail

ROOT = repo_root()

ALLOWED_ROOT_ENTRIES = {
    ".cargo",
    ".codex",
    ".github",
    ".gitignore",
    ".ssot",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "Cargo.lock",
    "Cargo.toml",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "bindings",
    "certification",
    "crates",
    "docs",
    "examples",
    "perf.sqlite",
    "pkgs",
    "pyproject.toml",
    "rust-toolchain.toml",
    "tools",
    "uv.lock",
}

ALLOWED_ROOT_ENTRY_PATTERNS = (
    re.compile(r"^\.tmp_run_[0-9]+_jobs\.json$"),
)

DISALLOWED_GENERATED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    "build",
    "dist",
    "site",
    "target",
    ".eggs",
    "htmlcov",
}

EXCLUDED_ROOTS = {
    ROOT / ".git",
    ROOT / ".pytest_cache",
    ROOT / ".venv",
    ROOT / ".tmp",
    ROOT / ".uv-cache",
    ROOT / ".uv-pytest",
    ROOT / ".uv-pytest-tigrbl-tests",
    ROOT / ".pip-cache",
    ROOT / ".benchmarks",
    ROOT / "target",
}

EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
}


def is_excluded(path: Path) -> bool:
    return any(path == ex or ex in path.parents for ex in EXCLUDED_ROOTS) or any(
        part in EXCLUDED_DIR_NAMES for part in path.relative_to(ROOT).parts
    )


def main() -> None:
    errors: list[str] = []

    root_entries = {p.name for p in ROOT.iterdir() if not is_excluded(p)}
    unexpected = sorted(
        name
        for name in root_entries - ALLOWED_ROOT_ENTRIES
        if not any(pattern.fullmatch(name) for pattern in ALLOWED_ROOT_ENTRY_PATTERNS)
    )
    if unexpected:
        errors.append(f"unexpected root entries: {', '.join(unexpected)}")

    for path in ROOT.rglob("*"):
        if not path.is_dir():
            continue
        if is_excluded(path):
            continue
        if path.name in DISALLOWED_GENERATED_DIR_NAMES:
            errors.append(f"generated or clutter directory present: {path.relative_to(ROOT)}")

    fail(errors)
    print("root clutter validation passed")


if __name__ == "__main__":
    main()
