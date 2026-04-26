from __future__ import annotations

import json
from pathlib import Path

from common import fail, repo_root
from policy_workflow_support import policy_workflow_runs_validator
from simple_yaml import load_yaml

ROOT = repo_root()
CLAIM_FILES = [
    ROOT / "certification" / "claims" / "current.yaml",
    ROOT / "certification" / "claims" / "target.yaml",
    ROOT / "certification" / "claims" / "blocked.yaml",
    ROOT / "certification" / "claims" / "evidenced.yaml",
]
LIFECYCLE = ROOT / "certification" / "claims" / "lifecycle.yaml"
BUNDLE = ROOT / "docs" / "conformance" / "releases" / "0.3.18" / "artifacts" / "certification-bundle.json"
CURRENT_STATE = ROOT / ".ssot" / "reports" / "current_state" / "2026-04-09-phase7-claims-evidence-promotion.md"
CERT_STATE = ROOT / ".ssot" / "reports" / "certification_state" / "2026-04-09-phase7-claims-evidence-promotion.md"
IMPLEMENTATION_MAP = ROOT / "docs" / "conformance" / "IMPLEMENTATION_MAP.md"
DOC_POINTERS = ROOT / "docs" / "governance" / "DOC_POINTERS.md"
CI_VALIDATION = ROOT / "docs" / "developer" / "CI_VALIDATION.md"
WORKFLOW = ROOT / ".github" / "workflows" / "policy-governance.yml"
GATE_MODEL = ROOT / "docs" / "conformance" / "GATE_MODEL.md"
ALLOWED_STATES = {"draft", "mapped", "implemented", "tested", "evidenced", "certified", "recertify_required"}
REQUIRED_FIELDS = (
    "boundary_inclusion",
    "target_mapping",
    "owning_modules",
    "adr_link",
    "public_contract_artifacts",
    "required_test_classes",
    "preserved_evidence",
    "release_gate_coverage",
)


def _read_yaml(path: Path) -> object:
    return load_yaml(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _public_claim_ids() -> set[str]:
    ids: set[str] = set()
    for path in CLAIM_FILES:
        payload = _read_yaml(path)
        if not isinstance(payload, dict):
            continue
        claims = payload.get("claims")
        if not isinstance(claims, list):
            continue
        for claim in claims:
            if isinstance(claim, dict) and claim.get("public") is True and isinstance(claim.get("id"), str):
                ids.add(claim["id"])
    return ids


def _path_exists(spec: str) -> bool:
    return (ROOT / spec.split("::", 1)[0].split("#", 1)[0]).exists()


def main() -> None:
    errors: list[str] = []
    public_claim_ids = _public_claim_ids()
    lifecycle = _read_yaml(LIFECYCLE)
    if not isinstance(lifecycle, dict):
        errors.append("certification/claims/lifecycle.yaml must be a mapping")
        fail(errors)
        return

    states = lifecycle.get("lifecycle_states")
    if not isinstance(states, list) or set(states) != ALLOWED_STATES:
        errors.append("certification/claims/lifecycle.yaml must declare the full draft..recertify_required lifecycle")

    claims = lifecycle.get("claims")
    if not isinstance(claims, list):
        errors.append("certification/claims/lifecycle.yaml must define claims as a list")
        fail(errors)
        return

    lifecycle_ids: set[str] = set()
    for entry in claims:
        if not isinstance(entry, dict):
            errors.append("certification/claims/lifecycle.yaml claim entries must be mappings")
            continue
        claim_id = entry.get("id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append("certification/claims/lifecycle.yaml entries must define id")
            continue
        lifecycle_ids.add(claim_id)
        state = entry.get("lifecycle")
        if state not in ALLOWED_STATES:
            errors.append(f"{claim_id} has invalid lifecycle state: {state}")
        for field in REQUIRED_FIELDS:
            value = entry.get(field)
            if field == "boundary_inclusion":
                if not isinstance(value, bool):
                    errors.append(f"{claim_id} must set boundary_inclusion to a boolean")
                elif state == "certified" and value is not True:
                    errors.append(f"{claim_id} must set boundary_inclusion: true before certification")
                continue
            if not value:
                errors.append(f"{claim_id} missing required lifecycle field: {field}")
                continue
            if isinstance(value, list):
                if field == "release_gate_coverage":
                    for item in value:
                        if item not in {"A", "B", "C", "D", "E"}:
                            errors.append(f"{claim_id} release_gate_coverage must only use A-E")
                    continue
                for item in value:
                    if not isinstance(item, str) or not _path_exists(item):
                        errors.append(f"{claim_id} references missing path in {field}: {item}")
            elif isinstance(value, str):
                if field in {"adr_link", "target_mapping"}:
                    if field == "adr_link" and not _path_exists(value):
                        errors.append(f"{claim_id} references missing adr_link: {value}")
                else:
                    if not _path_exists(value):
                        errors.append(f"{claim_id} references missing path in {field}: {value}")
        gates = entry.get("release_gate_coverage")
        if state == "certified" and isinstance(gates, list) and set(gates or []) != {"A", "B", "C", "D", "E"}:
            errors.append(f"{claim_id} must cover Gates A-E before reaching certified")

    missing = sorted(public_claim_ids - lifecycle_ids)
    if missing:
        errors.append(f"lifecycle registry missing public certification claims: {', '.join(missing)}")

    bundle = _read_json(BUNDLE)
    if not isinstance(bundle, dict):
        errors.append("release certification bundle must be a JSON object")
    else:
        for key in (
            "source_archive_digest",
            "built_artifacts",
            "spec_artifacts",
            "target_manifest",
            "claims_report",
            "evidence_manifest",
            "adr_index",
            "interop_bundle_references",
            "performance_artifacts",
            "attestation_provenance_records",
            "gate_decisions",
        ):
            if key not in bundle:
                errors.append(f"certification bundle missing key: {key}")
        for key in (
            "source_archive_digest",
            "spec_artifacts",
            "target_manifest",
            "claims_report",
            "evidence_manifest",
            "adr_index",
            "interop_bundle_references",
            "performance_artifacts",
            "attestation_provenance_records",
        ):
            value = bundle.get(key)
            if isinstance(value, str) and not _path_exists(value):
                errors.append(f"certification bundle references missing path: {value}")
        built = bundle.get("built_artifacts")
        if not isinstance(built, list) or not built:
            errors.append("certification bundle must declare built_artifacts")
        else:
            for item in built:
                if not isinstance(item, str) or not _path_exists(item):
                    errors.append(f"certification bundle references missing built artifact: {item}")
        gate_decisions = bundle.get("gate_decisions")
        expected = {
            "A": "surface freeze",
            "B": "correctness",
            "C": "interop",
            "D": "performance/operability",
            "E": "security/abuse",
        }
        if gate_decisions != expected:
            errors.append("certification bundle must map Gates A-E to the release decisions")

    current_state = _read_text(CURRENT_STATE)
    cert_state = _read_text(CERT_STATE)
    implementation_map = _read_text(IMPLEMENTATION_MAP)
    doc_pointers = _read_text(DOC_POINTERS)
    ci_validation = _read_text(CI_VALIDATION)
    workflow = _read_text(WORKFLOW)
    gate_model = _read_text(GATE_MODEL)

    if "claim lifecycle registry" not in current_state or "signed certification bundle" not in current_state:
        errors.append("Claim-lifecycle current-state report must describe the lifecycle registry and signed certification bundle")
    if "active `0.3.19.dev1` remains non-certifiable" not in cert_state:
        errors.append("Claim-lifecycle certification-state report must keep the active line non-certifiable")
    if "Claims, evidence, and certification-promotion checkpoint" not in implementation_map:
        errors.append("docs/conformance/IMPLEMENTATION_MAP.md must include the claim-lifecycle checkpoint row")
    if "Claim-lifecycle current-state report" not in doc_pointers or "Claim-lifecycle certification-state report" not in doc_pointers:
        errors.append("docs/governance/DOC_POINTERS.md must point to both claim-lifecycle reports")
    if "validate_claim_lifecycle.py" not in ci_validation:
        errors.append("docs/developer/CI_VALIDATION.md must list the claim-lifecycle validator")
    if not policy_workflow_runs_validator("validate_claim_lifecycle.py"):
        errors.append(".github/workflows/policy-governance.yml must run the claim-lifecycle validator")
    if "Gate A: surface freeze" not in gate_model or "Gate E: security/abuse" not in gate_model:
        errors.append("docs/conformance/GATE_MODEL.md must record the Release-decision mapping for Gates A-E")

    fail(errors)
    print("Claim-lifecycle validation passed")


if __name__ == "__main__":
    main()
