from __future__ import annotations

import json
from pathlib import Path

from common import repo_root, fail
from simple_yaml import load_yaml

ROOT = repo_root()
CERTIFICATION = ROOT / "certification"
BOUNDARY = CERTIFICATION / "boundary.yaml"
NEXT_TARGET = CERTIFICATION / "targets" / "next_target.yaml"
CLAIM_FILES = {
    "current": CERTIFICATION / "claims" / "current.yaml",
    "target": CERTIFICATION / "claims" / "target.yaml",
    "blocked": CERTIFICATION / "claims" / "blocked.yaml",
    "evidenced": CERTIFICATION / "claims" / "evidenced.yaml",
}
REQUIRED_TREE_PATHS = [
    CERTIFICATION / "boundary.yaml",
    CERTIFICATION / "targets" / "next_target.yaml",
    CERTIFICATION / "claims",
    CERTIFICATION / "gates",
    CERTIFICATION / "evidence" / "schema.json",
    CERTIFICATION / "profiles",
    ROOT / ".ssot" / "adr",
    ROOT / ".ssot" / "specs",
    ROOT / "reports" / "current_state",
    ROOT / "reports" / "certification_state",
]
REQUIRED_STATES = {"current", "target", "blocked", "evidenced"}
REQUIRED_FEATURE_FIELDS = {
    "owner",
    "package",
    "crate",
    "test_class",
    "claim_target",
    "evidence_artifacts",
}


def read_yaml(path: Path) -> object:
    return load_yaml(path.read_text(encoding="utf-8"))


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_boundary(errors: list[str]) -> dict[str, object]:
    boundary = read_yaml(BOUNDARY)
    if not isinstance(boundary, dict):
        errors.append("certification/boundary.yaml must be a mapping")
        return {}

    authority = boundary.get("authority")
    if not isinstance(authority, dict):
        errors.append("certification/boundary.yaml must define authority")
        return boundary

    if authority.get("authoritative") is not True:
        errors.append("certification/boundary.yaml must mark authority.authoritative: true")

    truth_model = authority.get("truth_model")
    if not isinstance(truth_model, dict):
        errors.append("certification/boundary.yaml must define authority.truth_model")
    else:
        states = truth_model.get("states")
        if not isinstance(states, list):
            errors.append("certification/boundary.yaml must define authority.truth_model.states as a list")
        else:
            found_states = {
                state.get("id")
                for state in states
                if isinstance(state, dict) and isinstance(state.get("id"), str)
            }
            if found_states != REQUIRED_STATES:
                errors.append(
                    "certification/boundary.yaml must define exactly the current/target/blocked/evidenced states"
                )

    authoritative_paths = authority.get("authoritative_paths")
    if not isinstance(authoritative_paths, dict):
        errors.append("certification/boundary.yaml must define authority.authoritative_paths")

    return boundary


def validate_evidence_schema(errors: list[str]) -> None:
    schema = load_json(CERTIFICATION / "evidence" / "schema.json")
    if not isinstance(schema, dict):
        errors.append("certification/evidence/schema.json must be a JSON object")
        return

    state_property = schema.get("properties", {}).get("state")
    if not isinstance(state_property, dict):
        errors.append("certification/evidence/schema.json must define properties.state")
        return

    enum_values = state_property.get("enum")
    if not isinstance(enum_values, list) or set(enum_values) != REQUIRED_STATES:
        errors.append("certification/evidence/schema.json must enumerate current/target/blocked/evidenced states")

    certified_boundary = schema.get("properties", {}).get("certified_boundary")
    if not isinstance(certified_boundary, dict) or certified_boundary.get("type") != "boolean":
        errors.append("certification/evidence/schema.json must define certified_boundary as a boolean")


def validate_claims(errors: list[str]) -> set[str]:
    claim_ids: set[str] = set()
    for state, path in CLAIM_FILES.items():
        payload = read_yaml(path)
        if not isinstance(payload, dict):
            errors.append(f"{path.relative_to(ROOT)} must be a mapping")
            continue
        if payload.get("state") != state:
            errors.append(f"{path.relative_to(ROOT)} must declare state: {state}")
        claims = payload.get("claims")
        if not isinstance(claims, list):
            errors.append(f"{path.relative_to(ROOT)} must define claims as a list")
            continue

        for index, claim in enumerate(claims, start=1):
            if not isinstance(claim, dict):
                errors.append(f"{path.relative_to(ROOT)} claim #{index} must be a mapping")
                continue
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append(f"{path.relative_to(ROOT)} claim #{index} must define a non-empty id")
                continue
            if claim_id in claim_ids:
                errors.append(f"duplicate certification claim id: {claim_id}")
            claim_ids.add(claim_id)

            public = claim.get("public")
            if public is True and "certified_boundary" not in claim:
                errors.append(f"{path.relative_to(ROOT)} claim {claim_id} must define certified_boundary for public claims")

    return claim_ids


def validate_next_target(errors: list[str], target_claim_ids: set[str]) -> None:
    payload = read_yaml(NEXT_TARGET)
    if not isinstance(payload, dict):
        errors.append("certification/targets/next_target.yaml must be a mapping")
        return
    if payload.get("status") != "target":
        errors.append("certification/targets/next_target.yaml must declare status: target")

    features = payload.get("features")
    if not isinstance(features, list) or not features:
        errors.append("certification/targets/next_target.yaml must define at least one feature")
    else:
        for feature in features:
            if not isinstance(feature, dict):
                errors.append("certification/targets/next_target.yaml features must be mappings")
                continue
            feature_id = feature.get("id", "<unknown>")
            missing = sorted(field for field in REQUIRED_FEATURE_FIELDS if not feature.get(field))
            if missing:
                errors.append(
                    f"certification/targets/next_target.yaml feature {feature_id} is missing required fields: {', '.join(missing)}"
                )
            claim_target = feature.get("claim_target")
            if isinstance(claim_target, str) and claim_target not in target_claim_ids:
                errors.append(
                    f"certification/targets/next_target.yaml feature {feature_id} points to unknown target claim {claim_target}"
                )
            evidence_artifacts = feature.get("evidence_artifacts")
            if not isinstance(evidence_artifacts, list) or not evidence_artifacts:
                errors.append(
                    f"certification/targets/next_target.yaml feature {feature_id} must define evidence_artifacts"
                )
            else:
                for artifact in evidence_artifacts:
                    if not isinstance(artifact, str) or not (ROOT / artifact).exists():
                        errors.append(
                            f"certification/targets/next_target.yaml feature {feature_id} references missing evidence artifact {artifact}"
                        )

    risks = payload.get("risks")
    if not isinstance(risks, list):
        errors.append("certification/targets/next_target.yaml must define risks as a list")
    else:
        for risk in risks:
            if not isinstance(risk, dict):
                errors.append("certification/targets/next_target.yaml risks must be mappings")
                continue
            if not risk.get("mitigation_owner"):
                errors.append(f"certification/targets/next_target.yaml risk {risk.get('id', '<unknown>')} must define mitigation_owner")

    issues = payload.get("issues")
    if not isinstance(issues, list):
        errors.append("certification/targets/next_target.yaml must define issues as a list")
    else:
        for issue in issues:
            if not isinstance(issue, dict):
                errors.append("certification/targets/next_target.yaml issues must be mappings")
                continue
            phase_link = issue.get("phase_link")
            waiver = issue.get("waiver")
            if not phase_link and not waiver:
                errors.append(
                    f"certification/targets/next_target.yaml issue {issue.get('id', '<unknown>')} must define phase_link or waiver"
                )

    phase_exit_criteria = payload.get("phase_exit_criteria")
    if not isinstance(phase_exit_criteria, dict):
        errors.append("certification/targets/next_target.yaml must define phase_exit_criteria")
    else:
        for key, value in phase_exit_criteria.items():
            if value is not True:
                errors.append(f"certification/targets/next_target.yaml phase_exit_criteria.{key} must be true")


def validate_required_paths(errors: list[str]) -> None:
    for path in REQUIRED_TREE_PATHS:
        if not path.exists():
            errors.append(f"missing certification authority path: {path.relative_to(ROOT)}")


def validate_reports(errors: list[str]) -> None:
    current_state_report = ROOT / "reports" / "current_state" / "2026-04-07-phase0-certification-freeze.md"
    certification_state_report = ROOT / "reports" / "certification_state" / "2026-04-07-registry-reclassification.md"

    current_state_text = current_state_report.read_text(encoding="utf-8")
    certification_state_text = certification_state_report.read_text(encoding="utf-8")

    if "certification-tree validator" not in current_state_text:
        errors.append("reports/current_state/2026-04-07-phase0-certification-freeze.md must record certification-tree validator status")
    if "machine-validated" not in certification_state_text:
        errors.append("reports/certification_state/2026-04-07-registry-reclassification.md must record machine-validated registry state")


def validate_lifecycle_completeness(errors: list[str]) -> None:
    lifecycle = read_yaml(CERTIFICATION / "claims" / "lifecycle.yaml")
    blocked = read_yaml(CERTIFICATION / "claims" / "blocked.yaml")
    if not isinstance(lifecycle, dict) or not isinstance(blocked, dict):
        errors.append("certification lifecycle and blocked claims must decode as mappings")
        return

    lifecycle_claims = lifecycle.get("claims")
    blocked_claims = blocked.get("claims")
    if not isinstance(lifecycle_claims, list) or not isinstance(blocked_claims, list):
        errors.append("certification lifecycle and blocked claims must define claims as lists")
        return

    lifecycle_ids = {
        entry.get("id")
        for entry in lifecycle_claims
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    for claim in blocked_claims:
        if not isinstance(claim, dict):
            continue
        claim_id = claim.get("id")
        if isinstance(claim_id, str) and claim_id not in lifecycle_ids:
            errors.append(
                f"blocked claim {claim_id} exists in certification/claims/blocked.yaml but not in certification/claims/lifecycle.yaml"
            )


def main() -> None:
    errors: list[str] = []

    validate_required_paths(errors)
    validate_boundary(errors)
    validate_evidence_schema(errors)
    claim_ids = validate_claims(errors)
    target_claim_ids = {
        claim_id
        for claim_id in claim_ids
        if claim_id.startswith("NEXT-")
    }
    validate_next_target(errors, target_claim_ids)
    validate_lifecycle_completeness(errors)
    validate_reports(errors)

    fail(errors)
    print("Certification authority tree validation passed")


if __name__ == "__main__":
    main()
