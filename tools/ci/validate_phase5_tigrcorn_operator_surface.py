from __future__ import annotations

from pathlib import Path

from common import fail, repo_root

ROOT = repo_root()
CURRENT_STATE = ROOT / "reports" / "current_state" / "2026-04-09-phase5-tigrcorn-operator-surface.md"
CERT_STATE = ROOT / "reports" / "certification_state" / "2026-04-09-phase5-tigrcorn-operator-surface.md"
CLI_REFERENCE = ROOT / "docs" / "developer" / "CLI_REFERENCE.md"
IMPLEMENTATION_MAP = ROOT / "docs" / "conformance" / "IMPLEMENTATION_MAP.md"
DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
CI_VALIDATION = ROOT / "docs" / "developer" / "CI_VALIDATION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"
BLOCKED_CLAIMS = ROOT / "certification" / "claims" / "blocked.yaml"
EXAMPLE_CONFIG = ROOT / "docs" / "developer" / "examples" / "tigrcorn" / "phase5-operator-config.json"
INTEROP_BUNDLE = ROOT / "docs" / "developer" / "examples" / "tigrcorn" / "phase5-interop-bundle-manifest.json"
BENCHMARK_BUNDLE = ROOT / "docs" / "developer" / "examples" / "tigrcorn" / "phase5-benchmark-bundle-manifest.json"


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
        "StatsD / DogStatsD export controls",
        "OpenTelemetry / tracing export controls",
        "graceful drain and shutdown timeout controls",
        "formal benchmark / throughput artifact bundle directories",
    ):
        if snippet not in current_state:
            errors.append(f"Phase 5 current-state report missing snippet: {snippet}")

    if "still not certifiably fully featured" not in current_state or "still not certifiably fully RFC compliant" not in current_state:
        errors.append("Phase 5 current-state report must keep the active-line certification limitation explicit")

    if "certification claims for them remain blocked until the bundles are populated by governed release evidence" not in cert_state:
        errors.append("Phase 5 certification-state report must keep interop/benchmark claims blocked pending release evidence")

    for snippet in (
        "--statsd-addr",
        "--otel-endpoint",
        "--concurrency-limit",
        "--http3-max-data",
        "--alpn-policy",
        "--interop-bundle-dir",
        "docs/developer/examples/tigrcorn/phase5-operator-config.json",
    ):
        if snippet not in cli_reference:
            errors.append(f"CLI reference missing Phase 5 Tigrcorn surface snippet: {snippet}")

    if "Phase 5 Tigrcorn operator surface checkpoint" not in implementation_map:
        errors.append("docs/conformance/IMPLEMENTATION_MAP.md must include the Phase 5 Tigrcorn operator surface checkpoint row")

    if "Phase 5 current-state report" not in doc_pointers or "Phase 5 certification-state report" not in doc_pointers:
        errors.append("docs/governance/DOC_POINTERS.md must point to both Phase 5 reports")

    if "validate_phase5_tigrcorn_operator_surface.py" not in ci_validation:
        errors.append("docs/developer/CI_VALIDATION.md must list the Phase 5 Tigrcorn operator-surface validator")

    if "Validate Phase 5 Tigrcorn operator surface" not in workflow:
        errors.append(".github/workflows/policy-governance.yml must run the Phase 5 Tigrcorn operator-surface validator")

    if "BLK-005" not in blocked_claims or "Tigrcorn interop and benchmark certification claims must remain blocked" not in blocked_claims:
        errors.append("certification/claims/blocked.yaml must block Tigrcorn interop/benchmark certification claims until release evidence exists")

    for path in (EXAMPLE_CONFIG, INTEROP_BUNDLE, BENCHMARK_BUNDLE):
        if not path.exists():
            errors.append(f"Missing Phase 5 example/bundle manifest: {path.relative_to(ROOT)}")

    fail(errors)
    print("Phase 5 Tigrcorn operator-surface validation passed")


if __name__ == "__main__":
    main()
