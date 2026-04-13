from __future__ import annotations

from pathlib import Path
import re
from common import repo_root, fail

ROOT = repo_root()

BANNED_PATTERNS = {
    r"\bcertified\b": "certified",
    r"\bcertifiably\b": "certifiably",
    r"\bconformant\b": "conformant",
    r"\bfully[- ]featured\b": "fully featured",
    r"\bfully compliant\b": "fully compliant",
}

EXCLUDED_PREFIXES = [
    Path("docs/governance"),
    Path("docs/conformance"),
    Path("docs/adr"),
    Path("docs/notes"),
]

SCAN_PATHS = [
    Path("README.md"),
    Path("CONTRIBUTING.md"),
    Path("CODE_OF_CONDUCT.md"),
    Path("SECURITY.md"),
    Path("docs/developer"),
    Path("docs/architecture"),
    Path("docs/migration"),
    Path("docs/testing"),
    Path("pkgs"),
    Path("crates"),
    Path("bindings/python"),
]


def should_skip(rel: Path) -> bool:
    return any(rel == prefix or prefix in rel.parents for prefix in EXCLUDED_PREFIXES)


def iter_markdown_files() -> list[Path]:
    files: list[Path] = []
    for base in SCAN_PATHS:
        path = ROOT / base
        if not path.exists():
            continue
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
            continue
        for file in path.rglob("*.md"):
            rel = file.relative_to(ROOT)
            if should_skip(rel):
                continue
            files.append(file)
    return sorted(set(files))


def main() -> None:
    errors: list[str] = []
    for file in iter_markdown_files():
        rel = file.relative_to(ROOT)
        text = file.read_text()
        for pattern, label in BANNED_PATTERNS.items():
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                line_no = text[: match.start()].count("\n") + 1
                errors.append(f"{rel}:{line_no} uses banned claim wording '{label}'")
    fail(errors)
    print("claim language lint passed")


if __name__ == "__main__":
    main()
