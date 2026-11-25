from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib


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


class _Images(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.images: list[dict[str, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


def _check_managed_badges(package_root: Path, readme: str, manifest: dict) -> str:
    project = manifest["project"]
    settings = manifest["tool"]["readme_standards"]
    name = project["name"]
    assert readme.splitlines()[0] == f"# {name}", package_root
    assert settings["policy"] == "package-guide-v1", package_root
    assert "readme-standards:begin branding" in readme, package_root
    images = _Images()
    images.feed(readme)
    alts = [image.get("alt", "") for image in images.images]
    for expected in (
        f"Source version: {project['version']}",
        f"Python: {project['requires-python']}",
        f"Layer: {settings['layer']}",
        "License: Apache-2.0",
        "Notice: attribution",
    ):
        assert alts.count(expected) == 1, (package_root, expected)
    hits = [
        image for image in images.images if image.get("alt") == f"README hits: {name}"
    ]
    assert len(hits) == 1, package_root
    relative = package_root.relative_to(ROOT).as_posix()
    target = f"https://hits.sh/github.com/tigrbl/tigrbl/{relative}/README.md.svg"
    assert hits[0]["src"].split("?", 1)[0] == target, package_root
    if settings["distributions"]["pypi"]["published"]:
        downloads = [
            image
            for image in images.images
            if image.get("alt") == f"Monthly PyPI downloads: {name}"
        ]
        assert len(downloads) == 1, package_root
        assert downloads[0]["src"].split("?", 1)[0] == f"https://img.shields.io/pypi/dm/{name}", (
            package_root
        )
    else:
        assert alts.count(f"pypi downloads: {name}: unpublished") == 1, package_root
    return target


def test_all_package_roots_have_required_legal_files_and_badges() -> None:
    package_roots = _package_roots()
    assert package_roots, "No package manifests discovered"

    hit_counters = set()
    for package_root in package_roots:
        readme = (package_root / "README.md").read_text(encoding="utf-8")

        assert (package_root / "LICENSE").exists(), package_root
        assert (package_root / "NOTICE").exists(), package_root
        manifest = tomllib.loads((package_root / "pyproject.toml").read_text("utf-8"))
        if manifest.get("tool", {}).get("readme_standards"):
            counter = _check_managed_badges(package_root, readme, manifest)
            assert counter not in hit_counters, package_root
            hit_counters.add(counter)
            continue
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
    assert facade_readme.splitlines()[0] == "# tigrbl"
    assert "pkgs/80_facade/tigrbl/README.md" in root_readme
    assert "<h1>Tigrbl Workspace</h1>" not in facade_readme
    assert "This root README is the repository and workspace entry point" in root_readme
