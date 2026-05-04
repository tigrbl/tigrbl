from __future__ import annotations

from collections.abc import Iterable
import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from common import repo_root

ROOT = repo_root()

POLICY_VALIDATORS = (
    "tools/ci/validate_package_layout.py",
    "tools/ci/validate_doc_pointers.py",
    "tools/ci/validate_root_clutter.py",
    "tools/ci/validate_path_lengths.py",
    "tools/ci/lint_claim_language.py",
    "tools/ci/validate_boundary_freeze_manifest.py",
    "tools/ci/enforce_boundary_freeze_diff.py",
    "tools/ci/lint_release_note_claims.py",
    "tools/ci/validate_evidence_registry.py",
    "tools/ci/validate_evidence_bundles.py",
    "tools/ci/validate_certification_tree.py",
    "tools/ci/validate_ssot_authority_model.py",
    "tools/ci/validate_declared_surface.py",
    "tools/ci/validate_rust_parity.py",
    "tools/ci/validate_tigrcorn_operator_surface.py",
    "tools/ci/validate_tigrcorn_hardening.py",
    "tools/ci/validate_claim_lifecycle.py",
    "tools/ci/validate_gate_b_surface_closure.py",
    "tools/ci/validate_gate_c_conformance_security.py",
    "tools/ci/validate_gate_d_reproducibility.py",
    "tools/ci/validate_gate_e_promotion.py",
    "tools/ci/validate_post_promotion_handoff.py",
)

DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
DOC_POINTER_CODE_RE = re.compile(r"`([^`]+)`")
POINTER_SECTION_MARKER = "## SSOT-First Reader Path"
NEXT_SECTION_PREFIX = "## "

REQUIRED_CANONICAL_DOCS = [
    "docs/README.md",
    "docs/conformance/CURRENT_TARGET.md",
    "docs/conformance/CURRENT_STATE.md",
    "docs/conformance/NEXT_STEPS.md",
    "docs/conformance/NEXT_TARGETS.md",
    "docs/governance/DOC_POINTERS.md",
    "docs/governance/PATH_LENGTH_POLICY.md",
    "docs/developer/PACKAGE_CATALOG.md",
    "docs/developer/PACKAGE_LAYOUT.md",
    "docs/developer/CI_VALIDATION.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
]

DISALLOWED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    ".tox",
    ".nox",
    ".eggs",
    "htmlcov",
    "build",
    "dist",
    "site",
    "target",
}

EXCLUDED_ROOTS = {
    ROOT / ".git",
    ROOT / ".venv",
    ROOT / ".tmp",
    ROOT / ".uv-cache",
    ROOT / ".uv-pytest",
    ROOT / ".uv-pytest-tigrbl-tests",
    ROOT / ".pip-cache",
    ROOT / ".benchmarks",
}

ROOT_TEMP_FILES = {
    "temp_adr_list.json",
    "temp_feature_list.json",
    "perf.sqlite",
}

ROOT_TEMP_FILE_PATTERNS = (
    re.compile(r"^\.tmp_run_[0-9]+_jobs\.json$"),
)


def _run_validation(script: str) -> tuple[int, str]:
    process = subprocess.run(
        [sys.executable, script],
        cwd=ROOT,
        env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        check=False,
        capture_output=True,
        text=True,
    )
    output = (process.stdout or "") + (process.stderr or "")
    return process.returncode, output


def _path_is_excluded(path: Path) -> bool:
    if path == ROOT:
        return False
    return any(excluded == path or excluded in path.parents for excluded in EXCLUDED_ROOTS)


def _remove_path(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        return True
    except OSError:
        return False


def _clean_root_clutter() -> int:
    removed = 0

    for name in sorted(ROOT_TEMP_FILES):
        if _remove_path(ROOT / name):
            removed += 1

    for path in ROOT.iterdir():
        if path.is_file() and any(pattern.fullmatch(path.name) for pattern in ROOT_TEMP_FILE_PATTERNS):
            if _remove_path(path):
                removed += 1

    stale_entries = []
    for path in ROOT.rglob("*"):
        if _path_is_excluded(path):
            continue
        if path.name in DISALLOWED_DIR_NAMES and path.is_dir():
            stale_entries.append(path)
        if path.is_file() and path.suffix in {".pyc", ".pyo"}:
            stale_entries.append(path)

    for path in sorted(stale_entries, key=lambda p: len(p.parts), reverse=True):
        if _remove_path(path):
            removed += 1

    return removed


def _fix_doc_pointers() -> int:
    if not DOC_POINTERS.exists():
        return 0

    text = DOC_POINTERS.read_text(encoding="utf-8")
    changed = 0
    fixed_text = text

    for match in DOC_POINTER_CODE_RE.finditer(text):
        target = match.group(1)
        if not target.startswith("reports/"):
            continue
        replacement = f".ssot/{target}"
        replacement_path = ROOT / replacement
        if replacement_path.exists():
            fixed_text = fixed_text.replace(f"`{target}`", f"`{replacement}`", 1)
            changed += 1

    if fixed_text != text:
        DOC_POINTERS.write_text(fixed_text, encoding="utf-8")
        text = fixed_text

    lines = DOC_POINTERS.read_text(encoding="utf-8").splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line == POINTER_SECTION_MARKER:
            start = idx + 1
            break
    if start is None:
        return changed

    end = start
    while end < len(lines) and not lines[end].startswith(NEXT_SECTION_PREFIX):
        end += 1

    seen = set(line.strip() for line in lines[start:end])
    additions: list[str] = []
    for doc in REQUIRED_CANONICAL_DOCS:
        entry = f"- `{doc}`"
        if entry not in seen:
            additions.append(entry)

    if additions:
        insert_at = end
        for entry in additions:
            lines.insert(insert_at, entry)
            insert_at += 1
            changed += 1
        DOC_POINTERS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return changed


def _validate(validators: Iterable[str] | None = None) -> list[str]:
    failures: list[str] = []
    scripts = tuple(validators or POLICY_VALIDATORS)
    for script in scripts:
        code, output = _run_validation(script)
        if code != 0:
            failures.append(f"{script}\n{output.strip()}")
    return failures


def _apply_fixes(failures: Iterable[str]) -> int:
    failed = {entry.splitlines()[0] for entry in failures}
    total = 0

    if any("validate_root_clutter.py" in failure for failure in failed):
        total += _clean_root_clutter()

    if any("validate_doc_pointers.py" in failure for failure in failed):
        total += _fix_doc_pointers()

    return total


def run(mode: str) -> int:
    failures = _validate(POLICY_VALIDATORS)
    if not failures:
        print("Policy governance validation passed.")
        return 0

    print("Policy governance validation failed:")
    for failure in failures:
        print(failure)

    if mode != "fix":
        return 1

    total_fixes = _apply_fixes(failures)
    if total_fixes:
        print(f"Applied {total_fixes} targeted policy governance fix(es).")
    else:
        print("No automated policy governance fixes were applicable.")

    print("Re-running policy governance validation...")
    failures = _validate(POLICY_VALIDATORS)
    if not failures:
        print("Policy governance validation passed after repair.")
        return 0

    print("Policy governance validation still failing after repair:")
    for failure in failures:
        print(failure)
    return 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("check", "fix"),
        default="check",
        help="Run check-only or validate then auto-fix and recheck.",
    )
    args = parser.parse_args()
    raise SystemExit(run(args.mode))


if __name__ == "__main__":
    main()
