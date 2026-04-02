from __future__ import annotations

from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()

ALLOWED_ROOT_ENTRIES = {
    ".cargo",
    ".github",
    ".gitignore",
    "CODE_OF_CONDUCT.md",
    "CONTRIBUTING.md",
    "Cargo.lock",
    "Cargo.toml",
    "LICENSE",
    "README.md",
    "SECURITY.md",
    "bindings",
    "crates",
    "docs",
    "pkgs",
    "pyproject.toml",
    "rust-toolchain.toml",
    "tools",
}

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
}


def is_excluded(path: Path) -> bool:
    return any(path == ex or ex in path.parents for ex in EXCLUDED_ROOTS)


def main() -> None:
    errors: list[str] = []

    root_entries = {p.name for p in ROOT.iterdir()}
    unexpected = sorted(root_entries - ALLOWED_ROOT_ENTRIES)
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
