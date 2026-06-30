from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PACKAGE_GLOBS = ("pkgs/*/*",)
PYTHON_BADGE_LABEL = "3.10 | 3.11 | 3.12 | 3.13 | 3.14"
REQUIRED_SECTIONS = (
    "## Certification Status",
    "## Install",
    "## Surface Coverage",
    "## What It Owns",
    "## Public API and Import Surface",
    "## Usage Examples",
    "## How To Choose This Package",
    "## Related Packages",
    "## Documentation Links",
    "## Support",
    "## License",
)
QUESTION_PREFIXES = (
    "## What is ",
    "## Why use ",
    "## When should I install ",
    "## Who is ",
    "## Where does ",
    "## How does ",
)


def _package_roots() -> list[Path]:
    roots: list[Path] = []
    for pattern in PACKAGE_GLOBS:
        roots.extend(
            path
            for path in ROOT.glob(pattern)
            if path.is_dir() and (path / "pyproject.toml").exists()
        )
    return sorted(roots)


def test_all_package_roots_have_required_legal_files_and_badges() -> None:
    package_roots = _package_roots()
    assert len(package_roots) == 42

    for package_root in package_roots:
        readme = (package_root / "README.md").read_text(encoding="utf-8")

        assert (package_root / "LICENSE").exists(), package_root
        assert (package_root / "NOTICE").exists(), package_root
        assert "license-Apache%202.0" in readme, package_root
        assert "discord.gg/K4YTAPapjR" in readme, package_root
        assert PYTHON_BADGE_LABEL in readme, package_root
        assert "## Quick Answers" not in readme, package_root
        for section in REQUIRED_SECTIONS:
            assert section in readme, (package_root, section)
        for prefix in QUESTION_PREFIXES:
            assert prefix in readme, (package_root, prefix)


def test_root_readme_and_facade_package_readme_are_distinct() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    facade_readme = (ROOT / "pkgs/80_facade/tigrbl/README.md").read_text(
        encoding="utf-8"
    )

    assert "<h1>Tigrbl Workspace</h1>" in root_readme
    assert "<h1>tigrbl</h1>" in facade_readme
    assert "pkgs/80_facade/tigrbl/README.md" in root_readme
    assert "<h1>Tigrbl Workspace</h1>" not in facade_readme
    assert "This root README is the repository and workspace entry point" in root_readme
