from __future__ import annotations

from pathlib import Path

from common import fail, repo_root

ROOT = repo_root()
CURRENT_STATE = ROOT / "reports" / "current_state" / "2026-04-09-phase4-native-parity.md"
CERT_STATE = ROOT / "reports" / "certification_state" / "2026-04-09-phase4-native-parity.md"
CONFORMANCE_PLAN = ROOT / "docs" / "testing" / "rust_conformance_plan.md"
IMPLEMENTATION_MAP = ROOT / "docs" / "conformance" / "IMPLEMENTATION_MAP.md"
DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
CI_VALIDATION = ROOT / "docs" / "developer" / "CI_VALIDATION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"
BLOCKED_CLAIMS = ROOT / "certification" / "claims" / "blocked.yaml"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    errors: list[str] = []

    current_state = _read(CURRENT_STATE)
    cert_state = _read(CERT_STATE)
    conformance_plan = _read(CONFORMANCE_PLAN)
    implementation_map = _read(IMPLEMENTATION_MAP)
    doc_pointers = _read(DOC_POINTERS)
    ci_validation = _read(CI_VALIDATION)
    workflow = _read(WORKFLOW)
    blocked_claims = _read(BLOCKED_CLAIMS)

    for snippet in (
        "route/opview/phase-plan parity snapshots",
        "differential Python-vs-native parity suites",
        "packed-plan parity",
        "REST, JSON-RPC, SSE, WS/WSS, and WebTransport transport traces",
    ):
        if snippet not in current_state:
            errors.append(f"Phase 4 current-state report missing snippet: {snippet}")

    if "does **not** justify claiming that the active `0.3.19.dev1` line is certifiably fully featured or certifiably fully RFC/spec compliant" not in current_state:
        errors.append("Phase 4 current-state report must keep the active-line certification limitation explicit")

    if "native backend claims remain blocked until the parity lanes are both implemented and passed as release evidence" not in cert_state:
        errors.append("Phase 4 certification-state report must explicitly keep Rust backend claims blocked")

    if "differential snapshots between Python and Rust kernel plans" not in conformance_plan:
        errors.append("docs/testing/rust_conformance_plan.md must continue to cover kernel parity snapshots")
    if "Rust backend remains non-claimable until the parity lanes pass as release evidence" not in conformance_plan:
        errors.append("docs/testing/rust_conformance_plan.md must keep Rust claimability fail-closed")

    if "Phase 4 rust parity checkpoint" not in implementation_map:
        errors.append("docs/conformance/IMPLEMENTATION_MAP.md must include the Phase 4 rust parity checkpoint row")

    if "Phase 4 current-state report" not in doc_pointers or "Phase 4 certification-state report" not in doc_pointers:
        errors.append("docs/governance/DOC_POINTERS.md must point to both Phase 4 reports")

    if "validate_phase4_rust_parity.py" not in ci_validation:
        errors.append("docs/developer/CI_VALIDATION.md must list the Phase 4 rust-parity validator")

    if "Validate Phase 4 rust parity" not in workflow:
        errors.append(".github/workflows/policy-governance.yml must run the Phase 4 rust-parity validator")

    if "BLK-004" not in blocked_claims or (
        "native backend claims must remain blocked" not in blocked_claims
        and "Rust backend claims must remain blocked" not in blocked_claims
    ):
        errors.append("certification/claims/blocked.yaml must block Rust backend claim publication until parity lanes pass")

    fail(errors)
    print("Phase 4 rust-parity validation passed")


if __name__ == "__main__":
    main()
