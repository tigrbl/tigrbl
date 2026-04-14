from __future__ import annotations

from pathlib import Path
import re
from common import repo_root, fail

ROOT = repo_root()

REQUIRED_CANONICAL_DOCS = [
    Path("docs/README.md"),
    Path("docs/conformance/CURRENT_TARGET.md"),
    Path("docs/conformance/CURRENT_STATE.md"),
    Path("docs/conformance/NEXT_STEPS.md"),
    Path("docs/conformance/NEXT_TARGETS.md"),
    Path("docs/governance/DOC_POINTERS.md"),
    Path("docs/governance/PATH_LENGTH_POLICY.md"),
    Path("docs/developer/PACKAGE_CATALOG.md"),
    Path("docs/developer/PACKAGE_LAYOUT.md"),
    Path("docs/developer/CI_VALIDATION.md"),
    Path("CONTRIBUTING.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path("SECURITY.md"),
]

ROOT_README_REQUIRED_STRINGS = [
    "docs/conformance/CURRENT_TARGET.md",
    "docs/conformance/CURRENT_STATE.md",
    "docs/conformance/NEXT_STEPS.md",
    "docs/governance/DOC_POINTERS.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
]

PACKAGE_README_REQUIRED_STRINGS = [
    "This file is a package-local distribution entry point.",
    "docs/README.md",
    "docs/conformance/CURRENT_TARGET.md",
    "docs/conformance/CURRENT_STATE.md",
    "docs/conformance/NEXT_STEPS.md",
    "docs/governance/DOC_POINTERS.md",
    "docs/developer/PACKAGE_CATALOG.md",
    "docs/developer/PACKAGE_LAYOUT.md",
]

POINTER_DOCS = [
    Path("README.md"),
    Path("docs/README.md"),
    Path("docs/governance/DOC_POINTERS.md"),
]

BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./\-]+(?:/|\.md|\.json))`")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
ROOT_RELATIVE_PREFIXES = {"docs", "pkgs", "crates", "tools", ".github", ".cargo"}
ROOT_RELATIVE_FILES = {
    "README.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "LICENSE",
    "Cargo.toml",
    "Cargo.lock",
    "pyproject.toml",
    "rust-toolchain.toml",
}


def package_readmes() -> list[Path]:
    patterns = [
        "pkgs/core/*/README.md",
        "pkgs/engines/*/README.md",
        "pkgs/apps/*/README.md",
        "crates/*/README.md",
    ]
    files: list[Path] = []
    for pattern in patterns:
        files.extend(sorted(ROOT.glob(pattern)))
    return [p for p in files if p.is_file()]


def iter_pointer_docs() -> list[Path]:
    docs = [ROOT / rel for rel in POINTER_DOCS]
    docs.extend(package_readmes())
    return sorted(set(docs))


def should_validate_doc_pointers_path(doc: Path, target: str) -> bool:
    rel_doc = doc.relative_to(ROOT)
    if rel_doc == Path("docs/governance/DOC_POINTERS.md"):
        return target.startswith("docs/") or target in ROOT_RELATIVE_FILES
    return True


def resolve_pointer(doc: Path, target: str) -> Path:
    first_segment = target.split("/", 1)[0]
    if target in ROOT_RELATIVE_FILES or first_segment in ROOT_RELATIVE_PREFIXES:
        return ROOT / target
    return doc.parent / target


def validate_pointer_target(doc: Path, target: str, errors: list[str]) -> None:
    if target.startswith(("http://", "https://", "mailto:")):
        return
    candidate = target.split("#", 1)[0]
    if not candidate or "YYYY" in candidate or not should_validate_doc_pointers_path(doc, candidate):
        return
    path = resolve_pointer(doc, candidate)
    if candidate.endswith("/"):
        if not path.is_dir():
            errors.append(f"{doc.relative_to(ROOT)} points to missing directory {candidate}")
    else:
        if not path.exists():
            errors.append(f"{doc.relative_to(ROOT)} points to missing path {candidate}")


def main() -> None:
    errors: list[str] = []

    for rel in REQUIRED_CANONICAL_DOCS:
        if not (ROOT / rel).is_file():
            errors.append(f"missing canonical document {rel}")

    root_readme = (ROOT / "README.md").read_text()
    for needle in ROOT_README_REQUIRED_STRINGS:
        if needle not in root_readme:
            errors.append(f"root README missing pointer to {needle}")

    docs_readme = (ROOT / "docs" / "README.md").read_text()
    for needle in [
        "conformance/CURRENT_TARGET.md",
        "conformance/CURRENT_STATE.md",
        "conformance/NEXT_STEPS.md",
        "conformance/NEXT_TARGETS.md",
        "governance/DOC_POINTERS.md",
    ]:
        if needle not in docs_readme:
            errors.append(f"docs/README.md missing pointer to {needle}")

    pointer_map = (ROOT / "docs" / "governance" / "DOC_POINTERS.md").read_text()
    for rel in REQUIRED_CANONICAL_DOCS:
        needle = rel.as_posix()
        if needle not in pointer_map and rel.name not in {"CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SECURITY.md"}:
            errors.append(f"DOC_POINTERS.md missing path {needle}")

    for readme in package_readmes():
        text = readme.read_text()
        for needle in PACKAGE_README_REQUIRED_STRINGS:
            if needle not in text:
                errors.append(f"{readme.relative_to(ROOT)} missing package pointer text: {needle}")

    for doc in iter_pointer_docs():
        text = doc.read_text()
        for target in BACKTICK_PATH_RE.findall(text):
            validate_pointer_target(doc, target, errors)
        for target in MARKDOWN_LINK_RE.findall(text):
            validate_pointer_target(doc, target, errors)

    fail(errors)
    print("doc pointer validation passed")


if __name__ == "__main__":
    main()
