from __future__ import annotations

from pathlib import Path

from common import repo_root, fail

ROOT = repo_root()
CURRENT_STATE = ROOT / "reports" / "current_state" / "2026-04-07-phase1-declarative-surface.md"
CERT_STATE = ROOT / "reports" / "certification_state" / "2026-04-07-phase1-declarative-surface.md"
DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
CI_VALIDATION = ROOT / "docs" / "developer" / "CI_VALIDATION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    errors: list[str] = []

    current_state = _read(CURRENT_STATE)
    cert_state = _read(CERT_STATE)
    doc_pointers = _read(DOC_POINTERS)
    ci_validation = _read(CI_VALIDATION)
    workflow = _read(WORKFLOW)

    for snippet in (
        "`Exchange`, `TxScope`, and `Framing` literals",
        "`HttpStreamBindingSpec`",
        "`SseBindingSpec`",
        "`WebTransportBindingSpec`",
        "docs-surface metadata sourced from declared bindings rather than handwritten approximations",
    ):
        if snippet not in current_state:
            errors.append(f"Phase 1 current-state report missing snippet: {snippet}")

    if "active `0.3.19.dev1` line is still not honestly describable as certifiably fully featured or certifiably fully RFC compliant" not in current_state:
        errors.append("Phase 1 current-state report must keep the active-line certification limitation explicit")

    if "active `0.3.19.dev1` remains a target/blocked line for certification purposes" not in cert_state:
        errors.append("Phase 1 certification-state report must keep the active line in target/blocked status")

    if "Phase 1 current-state report" not in doc_pointers or "Phase 1 certification-state report" not in doc_pointers:
        errors.append("docs/governance/DOC_POINTERS.md must point to both Phase 1 reports")

    if "validate_phase1_declared_surface.py" not in ci_validation:
        errors.append("docs/developer/CI_VALIDATION.md must list the Phase 1 declared-surface validator")

    if "Validate Phase 1 declared surface" not in workflow:
        errors.append(".github/workflows/policy-governance.yml must run the Phase 1 declared-surface validator")

    fail(errors)
    print("Phase 1 declared-surface validation passed")


if __name__ == "__main__":
    main()
