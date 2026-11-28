from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[6]

RETIREMENT_RECORDS = {
    ".ssot/adr/ADR-1002-package-dag-and-ownership.yaml",
    ".ssot/adr/ADR-1083-runtime-ddl-initialization-boundary.yaml",
    ".ssot/adr/ADR-1120-byte-oriented-runtime-execution-principles.yaml",
    ".ssot/adr/ADR-1185-python-only-runtime-and-rust-parity-retirement.yaml",
    ".ssot/specs/SPEC-2187-python-only-runtime-and-rust-retirement-contract.yaml",
}

FORBIDDEN_SUPPORT_PHRASES = (
    "optional rust runtime binding support",
    "optional rust/runtime-binding parity",
    "rust executor parity",
    "rust benchmark lanes",
    "tigrbl_rust_executor",
)


def _candidate_docs() -> list[Path]:
    candidates: list[Path] = [
        ROOT / "README.md",
        *ROOT.glob("docs/**/*.md"),
        *ROOT.glob("pkgs/**/README.md"),
        *ROOT.glob(".ssot/adr/*.yaml"),
        *ROOT.glob(".ssot/specs/*.yaml"),
    ]
    return [path for path in candidates if path.is_file()]


def test_docs_and_ssot_do_not_advertise_rust_parity_as_current_support() -> None:
    problems: list[str] = []
    for path in _candidate_docs():
        rel = path.relative_to(ROOT).as_posix()
        if rel in RETIREMENT_RECORDS:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_SUPPORT_PHRASES:
            if phrase in text:
                problems.append(f"{rel}: {phrase}")

    assert problems == []


def test_deprecated_rust_runtime_binding_doc_is_removed() -> None:
    assert not (ROOT / "docs/testing/rust_runtime_binding.md").exists()
