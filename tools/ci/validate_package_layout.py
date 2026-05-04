from __future__ import annotations

from pathlib import Path
from common import repo_root, fail

ROOT = repo_root()

PYTHON_PACKAGE_BASES = [
    ROOT / "pkgs" / "core",
    ROOT / "pkgs" / "engines",
    ROOT / "pkgs" / "apps",
]


def python_package_roots() -> list[Path]:
    package_roots: list[Path] = []
    for base in PYTHON_PACKAGE_BASES:
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if child.is_dir() and (child / "pyproject.toml").exists():
                package_roots.append(child)
    return package_roots


def rust_crate_roots() -> list[Path]:
    crates_dir = ROOT / "crates"
    if not crates_dir.exists():
        return []
    return [child for child in sorted(crates_dir.iterdir()) if child.is_dir() and (child / "Cargo.toml").exists()]


def markdown_allowed(path: Path, package_root: Path) -> bool:
    if any(part in {".pytest_cache", "__pycache__"} for part in path.parts):
        return True
    if package_root.name == "tigrbl_tests" and "perf" in path.relative_to(package_root).parts:
        return True
    return path == package_root / "README.md"


def main() -> None:
    errors: list[str] = []

    # category directories under pkgs should contain package dirs only
    for base in [ROOT / "pkgs" / "core", ROOT / "pkgs" / "engines", ROOT / "pkgs" / "apps"]:
        if not base.exists():
            continue
        for child in base.iterdir():
            if child.is_file():
                errors.append(f"category directory {base.relative_to(ROOT)} contains unexpected file {child.name}")

    # python package rules
    for package_root in python_package_roots():
        rel = package_root.relative_to(ROOT)
        package_name = package_root.name
        if not (package_root / "README.md").is_file():
            errors.append(f"{rel} missing README.md")
        src_layout = (package_root / "src" / package_name).is_dir()
        flat_layout = (package_root / package_name).is_dir()
        if src_layout == flat_layout:
            errors.append(
                f"{rel} must contain exactly one implementation layout: src/{package_name}/ or {package_name}/"
            )
        nested_pyprojects = [
            p.relative_to(ROOT)
            for p in package_root.rglob("pyproject.toml")
            if p != package_root / "pyproject.toml"
        ]
        if nested_pyprojects:
            errors.append(f"{rel} contains nested package roots: {', '.join(map(str, nested_pyprojects))}")
        disallowed_markdown = [
            p.relative_to(ROOT)
            for p in package_root.rglob("*.md")
            if not markdown_allowed(p, package_root)
        ]
        if disallowed_markdown:
            errors.append(f"{rel} contains non-authoritative Markdown files: {', '.join(map(str, disallowed_markdown))}")

    # rust crate rules
    for crate_root in rust_crate_roots():
        rel = crate_root.relative_to(ROOT)
        if not (crate_root / "README.md").is_file():
            errors.append(f"{rel} missing README.md")
        if not (crate_root / "src").is_dir():
            errors.append(f"{rel} missing src/")
        disallowed_markdown = [
            p.relative_to(ROOT)
            for p in crate_root.rglob("*.md")
            if p != crate_root / "README.md"
        ]
        if disallowed_markdown:
            errors.append(f"{rel} contains non-authoritative Markdown files: {', '.join(map(str, disallowed_markdown))}")

    fail(errors)
    print("package layout validation passed")


if __name__ == "__main__":
    main()
