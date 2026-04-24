from __future__ import annotations

from pathlib import Path

from common import fail, repo_root

ROOT = repo_root()
CURRENT_STATE = ROOT / ".ssot" / "reports" / "current_state" / "2026-04-09-phase6-tigrcorn-hardening.md"
CERT_STATE = ROOT / ".ssot" / "reports" / "certification_state" / "2026-04-09-phase6-tigrcorn-hardening.md"
CLI_REFERENCE = ROOT / "docs" / "developer" / "CLI_REFERENCE.md"
IMPLEMENTATION_MAP = ROOT / "docs" / "conformance" / "IMPLEMENTATION_MAP.md"
DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
CI_VALIDATION = ROOT / "docs" / "developer" / "CI_VALIDATION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"
BLOCKED_CLAIMS = ROOT / "certification" / "claims" / "blocked.yaml"
OPERATOR_PROFILES = ROOT / "docs" / "developer" / "operator" / "profiles"
PROFILE_REPORTS = ROOT / ".ssot" / "reports" / "certification_state" / "profiles"
NEGATIVE_CORPORA = ROOT / ".ssot" / "reports" / "certification_state" / "negative_corpora"
PROFILE_NAMES = (
    "strict-h1-origin",
    "strict-h2-origin",
    "strict-h3-edge",
    "strict-mtls-origin",
    "static-origin",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> None:
    errors: list[str] = []
    current_state = _read(CURRENT_STATE)
    cert_state = _read(CERT_STATE)
    cli_reference = _read(CLI_REFERENCE)
    implementation_map = _read(IMPLEMENTATION_MAP)
    doc_pointers = _read(DOC_POINTERS)
    ci_validation = _read(CI_VALIDATION)
    workflow = _read(WORKFLOW)
    blocked_claims = _read(BLOCKED_CLAIMS)

    for snippet in (
        "five blessed deployment profiles",
        "machine-readable profile documents",
        "profile-specific negative corpus manifests",
        "frozen proxy, early-data, and origin/pathsend/static contracts",
    ):
        if snippet not in current_state:
            errors.append(f"Tigrcorn hardening current-state report missing snippet: {snippet}")

    if "still not certifiably fully featured" not in current_state or "still not certifiably fully RFC compliant" not in current_state:
        errors.append("Tigrcorn hardening current-state report must keep the active-line certification limitation explicit")

    if "Profile claims remain blocked until profile-specific negative corpora and mixed-topology lanes are executed as governed release evidence" not in cert_state:
        errors.append("Tigrcorn hardening certification-state report must keep profile claims fail-closed")

    for snippet in (
        "--deployment-profile",
        "--proxy-contract",
        "--early-data-policy",
        "--origin-static-policy",
        "--quic-metrics",
        "--qlog-dir",
        "strict-h3-edge",
    ):
        if snippet not in cli_reference:
            errors.append(f"CLI reference missing Tigrcorn hardening snippet: {snippet}")

    if "Tigrcorn hardening and negative-certification checkpoint" not in implementation_map:
        errors.append("docs/conformance/IMPLEMENTATION_MAP.md must include the Tigrcorn hardening checkpoint row")

    if "Tigrcorn hardening current-state report" not in doc_pointers or "Tigrcorn hardening certification-state report" not in doc_pointers:
        errors.append("docs/governance/DOC_POINTERS.md must point to both Tigrcorn hardening reports")

    if "validate_tigrcorn_hardening.py" not in ci_validation:
        errors.append("docs/developer/CI_VALIDATION.md must list the Tigrcorn hardening validator")

    if "Validate Tigrcorn hardening" not in workflow:
        errors.append(".github/workflows/policy-governance.yml must run the Tigrcorn hardening validator")

    if "BLK-006" not in blocked_claims or "Tigrcorn hardening and negative-certification claims must remain blocked" not in blocked_claims:
        errors.append("certification/claims/blocked.yaml must block Tigrcorn hardening certification claims until release evidence exists")

    for name in PROFILE_NAMES:
        if not (OPERATOR_PROFILES / f"{name}.md").exists():
            errors.append(f"Missing operator profile page: docs/developer/operator/profiles/{name}.md")
        if not (PROFILE_REPORTS / f"{name}.profile.json").exists():
            errors.append(f"Missing machine-readable profile document: reports/certification_state/profiles/{name}.profile.json")
        if not (PROFILE_REPORTS / f"{name}.report.md").exists():
            errors.append(f"Missing profile certification report: reports/certification_state/profiles/{name}.report.md")
        if not (NEGATIVE_CORPORA / f"{name}.negative.json").exists():
            errors.append(f"Missing profile negative corpus: reports/certification_state/negative_corpora/{name}.negative.json")

    fail(errors)
    print("Tigrcorn hardening validation passed")


if __name__ == "__main__":
    main()
