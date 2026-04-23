from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
CONFORMANCE = ROOT / 'docs' / 'conformance'
DEV_VERSION = '0.3.18.dev1'
RELEASE_VERSION = '0.3.17'
DEV_ROOT = CONFORMANCE / 'dev' / DEV_VERSION
RELEASE_ROOT = CONFORMANCE / 'releases' / RELEASE_VERSION
CURRENT_DATE = '2026-03-31'

CLAIM_ROW_RE = re.compile(r'^\|\s*([A-Z0-9-]+)\s*\|')


@dataclass(frozen=True)
class EvidenceTemplate:
    lane_classes: list[str]
    tests: list[str]
    ci_jobs: list[str]
    artifact_paths: list[str]
    doc_paths: list[str]


GROUPS: dict[str, EvidenceTemplate] = {
    'governance': EvidenceTemplate(
        lane_classes=['policy governance', 'unit'],
        tests=[
            'tools/ci/tests/test_governance_validators.py::test_repo_governance_scripts_pass',
            'tools/ci/tests/test_path_length_policy.py::test_repository_conforms_to_declared_path_limits',
            'tools/ci/tests/test_evidence_registry.py::test_evidence_registry_and_bundle_validators_pass',
        ],
        ci_jobs=[
            '.github/workflows/policy-governance.yml#validate-policy',
            '.github/workflows/evidence-lanes.yml#evidence-lane[unit]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/policy-governance.md',
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/evidence-model.md',
        ],
        doc_paths=[
            'docs/conformance/CLAIM_REGISTRY.md',
            'docs/conformance/EVIDENCE_MODEL.md',
            'docs/conformance/EVIDENCE_REGISTRY.json',
        ],
    ),
    'spec': EvidenceTemplate(
        lane_classes=['unit', 'integration', 'spec conformance', 'docs UI smoke'],
        tests=[
            'pkgs/core/tigrbl_tests/tests/unit/test_spec_snapshots.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py',
            'pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py',
            'pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py',
            'pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py',
            'pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py',
        ],
        ci_jobs=[
            '.github/workflows/evidence-lanes.yml#evidence-lane[spec-conformance]',
            '.github/workflows/evidence-lanes.yml#evidence-lane[integration]',
            '.github/workflows/evidence-lanes.yml#evidence-lane[docs-ui-smoke]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/spec-conformance.md',
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/docs-ui-smoke.md',
        ],
        doc_paths=[
            'docs/conformance/CURRENT_TARGET.md',
            'docs/conformance/CURRENT_STATE.md',
            'docs/conformance/IMPLEMENTATION_MAP.md',
        ],
    ),
    'security': EvidenceTemplate(
        lane_classes=['security / negative', 'unit'],
        tests=[
            'pkgs/core/tigrbl_tests/tests/security/test_schemes.py',
            'tools/ci/tests/test_http_auth_challenges.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_authorize_runtime_secdep.py',
        ],
        ci_jobs=[
            '.github/workflows/evidence-lanes.yml#evidence-lane[security-negative]',
            '.github/workflows/policy-governance.yml#validate-policy',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/security-negative.md',
        ],
        doc_paths=[
            'docs/conformance/RFC_SECURITY_EVIDENCE_MAP.md',
            'docs/conformance/CURRENT_TARGET.md',
        ],
    ),
    'operator': EvidenceTemplate(
        lane_classes=['operator-surface smoke', 'docs UI smoke'],
        tests=[
            'pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_closure.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_operator_surface_docs_parity.py',
        ],
        ci_jobs=[
            '.github/workflows/operator-surface.yml#phase7-operator-surface',
            '.github/workflows/evidence-lanes.yml#evidence-lane[operator-surface-smoke]',
            '.github/workflows/evidence-lanes.yml#evidence-lane[docs-ui-smoke]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/operator-surface-smoke.md',
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/docs-ui-smoke.md',
        ],
        doc_paths=[
            'docs/developer/OPERATOR_SURFACES.md',
            'docs/developer/operator/README.md',
            'docs/conformance/CURRENT_TARGET.md',
        ],
    ),
    'cli': EvidenceTemplate(
        lane_classes=['CLI smoke', 'server compatibility smoke'],
        tests=[
            'pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py',
            'pkgs/core/tigrbl_tests/tests/unit/test_cli_srv.py',
        ],
        ci_jobs=[
            '.github/workflows/cli-smoke.yml#phase8-cli',
            '.github/workflows/evidence-lanes.yml#evidence-lane[cli-smoke]',
            '.github/workflows/evidence-lanes.yml#evidence-lane[server-compat-smoke]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/cli-smoke.md',
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/server-compat-smoke.md',
        ],
        doc_paths=[
            'docs/developer/CLI_REFERENCE.md',
            'docs/conformance/CURRENT_TARGET.md',
        ],
    ),
    'evidence': EvidenceTemplate(
        lane_classes=['unit', 'policy governance'],
        tests=[
            'tools/ci/tests/test_evidence_registry.py::test_claim_registry_rows_are_covered_by_evidence_registry',
            'tools/ci/tests/test_evidence_registry.py::test_evidence_registry_and_bundle_validators_pass',
        ],
        ci_jobs=[
            '.github/workflows/policy-governance.yml#validate-policy',
            '.github/workflows/evidence-lanes.yml#evidence-lane[unit]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/evidence-model.md',
        ],
        doc_paths=[
            'docs/conformance/EVIDENCE_MODEL.md',
            'docs/conformance/EVIDENCE_REGISTRY.json',
            f'docs/conformance/dev/{DEV_VERSION}/EVIDENCE_INDEX.md',
            f'docs/conformance/releases/{RELEASE_VERSION}/EVIDENCE_INDEX.md',
        ],
    ),
    'clean_room': EvidenceTemplate(
        lane_classes=['clean-room package tests'],
        tests=[
            'tools/conformance/clean_room_package_smoke.py',
            'tools/ci/tests/test_evidence_registry.py::test_evidence_registry_and_bundle_validators_pass',
        ],
        ci_jobs=[
            '.github/workflows/evidence-lanes.yml#evidence-lane[clean-room-package]',
        ],
        artifact_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/gate-results/clean-room-package.md',
            f'docs/conformance/releases/{RELEASE_VERSION}/artifacts/artifact-manifest.json',
        ],
        doc_paths=[
            f'docs/conformance/dev/{DEV_VERSION}/BUILD_NOTES.md',
            f'docs/conformance/releases/{RELEASE_VERSION}/EVIDENCE_INDEX.md',
        ],
    ),
}


CLAIM_OVERRIDES: dict[str, dict[str, list[str]]] = {
    'HANDOFF-001': {
        'lane_classes': ['post-promotion handoff', 'policy governance'],
        'tests': [
            'tools/ci/tests/test_post_promotion_handoff.py::test_post_promotion_handoff_validator_passes',
            'tools/ci/tests/test_post_promotion_handoff.py::test_current_docs_record_active_dev_line_and_frozen_release_history',
        ],
        'ci_jobs': [
            '.github/workflows/post-promotion-handoff.yml#post-promotion-handoff',
            '.github/workflows/policy-governance.yml#validate-policy',
        ],
        'artifact_paths': [
            'docs/conformance/dev/0.3.19.dev1/gate-results/post-promotion-handoff.md',
            'docs/conformance/audit/2026/post-promotion-handoff/README.md',
        ],
        'doc_paths': [
            'docs/conformance/CURRENT_TARGET.md',
            'docs/conformance/CURRENT_STATE.md',
            'docs/conformance/NEXT_TARGETS.md',
            'docs/conformance/dev/0.3.19.dev1/EVIDENCE_INDEX.md',
        ],
    },
    'HANDOFF-002': {
        'lane_classes': ['post-promotion handoff'],
        'tests': ['tools/ci/tests/test_post_promotion_handoff.py::test_post_promotion_handoff_validator_passes'],
        'ci_jobs': ['.github/workflows/post-promotion-handoff.yml#post-promotion-handoff'],
        'artifact_paths': ['docs/conformance/audit/2026/post-promotion-handoff/README.md'],
        'doc_paths': [
            'tools/ci/validate_post_promotion_handoff.py',
            'tools/ci/tests/test_post_promotion_handoff.py',
            '.github/workflows/post-promotion-handoff.yml',
            'docs/developer/CI_VALIDATION.md',
        ],
    },
    'NEXT-001': {
        'lane_classes': ['post-promotion handoff', 'policy governance'],
        'tests': [
            'tools/ci/tests/test_post_promotion_handoff.py::test_next_line_and_next_target_claim_rows_exist',
            'tools/ci/tests/test_post_promotion_handoff.py::test_current_docs_record_active_dev_line_and_frozen_release_history',
        ],
        'ci_jobs': [
            '.github/workflows/post-promotion-handoff.yml#post-promotion-handoff',
            '.github/workflows/policy-governance.yml#validate-policy',
        ],
        'artifact_paths': [
            'docs/conformance/dev/0.3.19.dev1/BUILD_NOTES.md',
            'docs/conformance/dev/0.3.19.dev1/EVIDENCE_INDEX.md',
        ],
        'doc_paths': [
            'pkgs/core/tigrbl/pyproject.toml',
            'docs/governance/VERSIONING_POLICY.md',
            'docs/conformance/CURRENT_STATE.md',
            'docs/conformance/dev/README.md',
        ],
    },
    'NEXT-002': {
        'lane_classes': ['post-promotion handoff'],
        'tests': [
            'tools/ci/tests/test_post_promotion_handoff.py::test_next_line_and_next_target_claim_rows_exist',
            'tools/ci/tests/test_post_promotion_handoff.py::test_post_promotion_handoff_validator_passes',
        ],
        'ci_jobs': ['.github/workflows/post-promotion-handoff.yml#post-promotion-handoff'],
        'artifact_paths': [
            'docs/conformance/NEXT_TARGETS.md',
            'docs/notes/archive/2026/post-promotion-handoff/README.md',
        ],
        'doc_paths': [
            'docs/conformance/NEXT_TARGETS.md',
            '.ssot/adr/ADR-1042-deferred-next-target-datatype-table-program.yaml',
            '.ssot/adr/ADR-1043-post-promotion-release-history-freeze.yaml',
            '.ssot/adr/ADR-1044-next-target-datatype-table-program-activation.yaml',
        ],
    },
    'NEXT-003': {
        'lane_classes': ['policy governance'],
        'tests': ['pkgs/core/tigrbl_tests/tests/unit/decorators/test_declarative_surface.py::test_declarative_surface_literals_are_present'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py'],
        'doc_paths': [
            'pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py',
            'pkgs/core/tigrbl_concrete/tigrbl_concrete/_decorators/op.py',
            'pkgs/core/tigrbl_concrete/tigrbl_concrete/_decorators/hook.py',
        ],
    },
    'NEXT-004': {
        'lane_classes': ['policy governance'],
        'tests': [
            'pkgs/core/tigrbl_tests/tests/unit/test_declared_surface_docs.py::test_declared_surface_docs_derive_from_bindings',
            'pkgs/core/tigrbl_concrete/tests/test_phase2_transport_docs.py::test_transport_docs_follow_declared_bindings',
        ],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['pkgs/core/tigrbl/tigrbl/system/docs/openapi/schema.py'],
        'doc_paths': [
            'pkgs/core/tigrbl/tigrbl/system/docs/openapi/schema.py',
            'pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/openrpc.py',
            'pkgs/core/tigrbl_concrete/tigrbl_concrete/system/docs/asyncapi.py',
        ],
    },
    'NEXT-005': {
        'lane_classes': ['policy governance'],
        'tests': ['tools/ci/tests/test_declared_surface.py::test_phase1_declared_surface_validator_passes'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['tools/ci/validate_declared_surface.py'],
        'doc_paths': ['tools/ci/validate_declared_surface.py', 'docs/developer/CI_VALIDATION.md'],
    },
    'NEXT-006': {
        'lane_classes': ['policy governance'],
        'tests': ['tools/ci/tests/test_transport_dispatch_track.py::test_transport_dispatch_track_validator_passes'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': [
            '.ssot/reports/transport-dispatch-track-setup.md',
            '.ssot/releases/boundaries/bnd_transport-dispatch-track-001.snapshot.json',
        ],
        'doc_paths': [
            'docs/conformance/NEXT_TARGETS.md',
            '.ssot/adr/ADR-1045-transport-dispatch-track-boundary-and-sequencing.yaml',
            '.ssot/specs/SPEC-2013-transport-ingress-single-dispatch-flow.yaml',
        ],
    },
    'NEXT-007': {
        'lane_classes': ['next-target planning'],
        'tests': ['pkgs/core/tigrbl_kernel/tests/test_transport_dispatch_kernelplan_contract.py::test_kernelplan_owns_transport_lookup_and_matching'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.yaml'],
        'doc_paths': [
            '.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.yaml',
            '.ssot/specs/SPEC-2013-transport-ingress-single-dispatch-flow.yaml',
        ],
    },
    'NEXT-008': {
        'lane_classes': ['next-target planning'],
        'tests': ['pkgs/core/tigrbl_core/tests/test_jsonrpc_endpoint_binding_spec_contract.py::test_http_jsonrpc_binding_spec_exposes_endpoint_identity'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.yaml'],
        'doc_paths': [
            '.ssot/adr/ADR-1046-endpoint-keyed-multiplexed-transport-bindings.yaml',
            '.ssot/specs/SPEC-2015-endpoint-keyed-jsonrpc-bindings.yaml',
            '.ssot/specs/SPEC-2016-core-default-endpoint-mappings.yaml',
        ],
    },
    'NEXT-009': {
        'lane_classes': ['next-target planning'],
        'tests': [
            'pkgs/core/tigrbl_kernel/tests/test_transport_dispatch_kernelplan_contract.py::test_kernelplan_owns_transport_lookup_and_matching',
            'pkgs/core/tigrbl_core/tests/test_jsonrpc_endpoint_binding_spec_contract.py::test_http_jsonrpc_binding_spec_exposes_endpoint_identity',
        ],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['.ssot/specs/SPEC-2014-binding-driven-rest-jsonrpc-materialization.yaml'],
        'doc_paths': ['.ssot/specs/SPEC-2014-binding-driven-rest-jsonrpc-materialization.yaml'],
    },
    'NEXT-010': {
        'lane_classes': ['next-target planning'],
        'tests': ['pkgs/core/tigrbl_kernel/tests/test_transport_dispatch_kernelplan_contract.py::test_kernelplan_owns_transport_lookup_and_matching'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.yaml'],
        'doc_paths': ['.ssot/adr/ADR-1047-kernelplan-owned-transport-dispatch.yaml'],
    },
    'NEXT-011': {
        'lane_classes': ['next-target planning'],
        'tests': ['tools/ci/tests/test_transport_dispatch_track.py::test_transport_dispatch_track_validator_passes'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': ['.ssot/releases/boundaries/bnd_transport-dispatch-track-001.snapshot.json'],
        'doc_paths': [
            '.ssot/registry.json',
            '.ssot/releases/boundaries/bnd_transport-dispatch-track-001.snapshot.json',
        ],
    },
    'NEXT-012': {
        'lane_classes': ['policy governance'],
        'tests': ['tools/ci/tests/test_transport_dispatch_track.py::test_transport_dispatch_track_validator_passes'],
        'ci_jobs': ['.github/workflows/policy-governance.yml#validate-policy'],
        'artifact_paths': [
            'tools/ci/validate_transport_dispatch_track.py',
            'docs/conformance/EVIDENCE_REGISTRY.json',
        ],
        'doc_paths': [
            'tools/ci/validate_transport_dispatch_track.py',
            'docs/conformance/EVIDENCE_REGISTRY.json',
        ],
    },
}


def parse_claim_ids() -> list[str]:
    ids: list[str] = []
    for line in (CONFORMANCE / 'CLAIM_REGISTRY.md').read_text(encoding='utf-8').splitlines():
        match = CLAIM_ROW_RE.match(line)
        if not match:
            continue
        claim_id = match.group(1).strip()
        if claim_id in {'Claim ID', '---'}:
            continue
        if re.match(r'^(?:[A-Z]+-\d+|RFC-\d+|OIDC-\d+)$', claim_id):
            ids.append(claim_id)
    return ids


def classify(claim_id: str) -> str:
    if claim_id.startswith(('GOV-', 'PATH-', 'GATE-')):
        return 'governance'
    if claim_id.startswith('OAS-') or claim_id.startswith('RPC-'):
        return 'spec'
    if claim_id.startswith('SEC-') or claim_id in {'RFC-7235', 'RFC-7617', 'RFC-6750'}:
        return 'security'
    if claim_id.startswith('OP-'):
        return 'operator'
    if claim_id.startswith('CLI-'):
        return 'cli'
    if claim_id == 'EVID-005':
        return 'clean_room'
    if claim_id.startswith('EVID-'):
        return 'evidence'
    if claim_id.startswith('CERT-'):
        return 'evidence'
    if claim_id in {'RFC-6749', 'RFC-7519', 'RFC-7636', 'RFC-8414', 'RFC-8705', 'RFC-9110', 'RFC-9449', 'OIDC-001'}:
        return 'evidence'
    raise KeyError(f'no evidence group mapping for {claim_id}')


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + '\n', encoding='utf-8')


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_registry() -> dict[str, object]:
    claims: dict[str, object] = {}
    for claim_id in parse_claim_ids():
        if claim_id in CLAIM_OVERRIDES:
            claims[claim_id] = CLAIM_OVERRIDES[claim_id]
            continue
        template = GROUPS[classify(claim_id)]
        claims[claim_id] = {
            'lane_classes': template.lane_classes,
            'tests': template.tests,
            'ci_jobs': template.ci_jobs,
            'artifact_paths': template.artifact_paths,
            'doc_paths': template.doc_paths,
        }
    return {
        'schema_version': 1,
        'generated_at': CURRENT_DATE,
        'dev_bundle': rel(DEV_ROOT),
        'release_bundle': rel(RELEASE_ROOT),
        'claims': claims,
    }


def build_gate_results_docs() -> None:
    dev_gate = DEV_ROOT / 'gate-results'
    release_gate = RELEASE_ROOT / 'gate-results'
    release_artifacts = RELEASE_ROOT / 'artifacts'

    summaries = {
        'policy-governance.md': '''# Policy Governance

This gate-result file records the governance validation lane used by the current checkpoint.

## Source validators

- `tools/ci/validate_package_layout.py`
- `tools/ci/validate_doc_pointers.py`
- `tools/ci/validate_root_clutter.py`
- `tools/ci/validate_path_lengths.py`
- `tools/ci/lint_claim_language.py`
- `tools/ci/validate_boundary_freeze_manifest.py`
- `tools/ci/lint_release_note_claims.py`
- `tools/ci/validate_evidence_registry.py`
- `tools/ci/validate_evidence_bundles.py`

## Source audit logs

- `docs/conformance/audit/2026/p9-evidence/validate_package_layout.log`
- `docs/conformance/audit/2026/p9-evidence/validate_doc_pointers.log`
- `docs/conformance/audit/2026/p9-evidence/validate_root_clutter.log`
- `docs/conformance/audit/2026/p9-evidence/validate_path_lengths.log`
- `docs/conformance/audit/2026/p9-evidence/lint_claim_language.log`
- `docs/conformance/audit/2026/p9-evidence/validate_boundary_freeze_manifest.log`
- `docs/conformance/audit/2026/p9-evidence/lint_release_note_claims.log`
- `docs/conformance/audit/2026/p9-evidence/validate_evidence_registry.log`
- `docs/conformance/audit/2026/p9-evidence/validate_evidence_bundles.log`
''',
        'unit.md': '''# Unit Lane

This lane aggregates the current checkpoint's representative unit-level proof.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_spec_snapshots.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py`
- `tools/ci/tests/test_evidence_registry.py`

## Source audit logs

- `docs/conformance/audit/2026/p9-evidence/pytest_evidence_registry.log`
- `docs/conformance/audit/2026/p8-cli/p8_cli_pytest.log`
- `docs/conformance/audit/2026/docs-spec-snapshot-closure/phase5_targeted_pytest.log`
''',
        'integration.md': '''# Integration Lane

This lane keeps the integration evidence paths visible and durable.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py`

## Source audit logs

- `docs/conformance/audit/2026/docs-spec-snapshot-closure/phase5_targeted_pytest.log`
- `docs/conformance/audit/2026/phase7-operator-surface/phase7_operator_pytest.log`
''',
        'spec-conformance.md': '''# Spec Conformance Lane

This lane covers OpenAPI, JSON Schema, JSON-RPC, and OpenRPC conformance evidence.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_spec_snapshots.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_openapi_documentation_security_behavior.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_openrpc_documentation_security_behavior.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_docs_security_parity.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`

## Source audit logs

- `docs/conformance/audit/2026/docs-spec-snapshot-closure/phase5_targeted_pytest.log`
- `docs/conformance/audit/2026/docs-spec-snapshot-closure/generate_spec_snapshots.log`
''',
        'security-negative.md': '''# Security / Negative Lane

This lane covers retained HTTP auth behavior, security negative tests, and challenge/header semantics.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/security/test_schemes.py`
- `tools/ci/tests/test_http_auth_challenges.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_authorize_runtime_secdep.py`

## Source audit logs

- `docs/conformance/audit/2026/p6-rfc-sec/test_http_auth_challenges.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_security_negative.log`
''',
        'docs-ui-smoke.md': '''# Docs UI Smoke Lane

This lane covers the mounted docs/spec endpoints and parity docs.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openapi_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_swagger_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_openrpc_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/i9n/test_mountable_lens_uvicorn.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py`

## Source audit logs

- `docs/conformance/audit/2026/phase7-operator-surface/phase7_operator_pytest.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_docs_ui_smoke.log`
''',
        'cli-smoke.md': '''# CLI Smoke Lane

This lane covers the unified `tigrbl` CLI command and flag smoke.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_cli_cmds.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py`

## Source audit logs

- `docs/conformance/audit/2026/p8-cli/p8_cli_pytest.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_cli_smoke.log`
''',
        'operator-surface-smoke.md': '''# Operator-Surface Smoke Lane

This lane covers the current operator-surface closure tests.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py`
- `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_docs_parity.py`

## Source audit logs

- `docs/conformance/audit/2026/phase7-operator-surface/phase7_operator_pytest.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_operator_surface.log`
''',
        'server-compat-smoke.md': '''# Server Compatibility Smoke Lane

This lane covers supported-server smoke at the current checkpoint quality level.

## Current meaning

The current server-compatibility lane verifies runner dispatch and governed flag/config translation for:

- Uvicorn
- Hypercorn
- Gunicorn
- Tigrcorn

It does **not** yet claim full live-network or clean-room installed-package compatibility certification.

## Primary tests

- `pkgs/core/tigrbl_tests/tests/unit/test_phase8_cli_srv.py`

## Source audit logs

- `docs/conformance/audit/2026/p8-cli/p8_cli_pytest.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_server_compat.log`
''',
        'clean-room-package.md': '''# Clean-Room Package Lane

This lane records the clean-room packaging/build scaffold added in Phase 9.

## Current meaning

At this checkpoint, the lane verifies:

- source distribution build
- wheel build
- package metadata inspection
- console entry-point presence in wheel metadata

It does **not** yet claim the later Gate D full installed-package multi-lane certification.

## Source script

- `tools/conformance/clean_room_package_smoke.py`

## Source audit logs

- `docs/conformance/audit/2026/p9-evidence/clean_room_package.log`
''',
        'evidence-model.md': '''# Evidence Model

This gate-result file records the durable evidence-model scaffolding introduced in Phase 9.

## Source documents

- `docs/conformance/EVIDENCE_MODEL.md`
- `docs/conformance/EVIDENCE_REGISTRY.json`
- `docs/conformance/dev/0.3.18.dev1/BUILD_NOTES.md`
- `docs/conformance/dev/0.3.18.dev1/EVIDENCE_INDEX.md`
- `docs/conformance/dev/0.3.18.dev1/CLAIMS.md`
- `docs/conformance/releases/0.3.17/RELEASE_NOTES.md`
- `docs/conformance/releases/0.3.17/CLAIMS.md`
- `docs/conformance/releases/0.3.17/EVIDENCE_INDEX.md`
- `docs/conformance/releases/0.3.17/CURRENT_TARGET_SNAPSHOT.md`

## Source audit logs

- `docs/conformance/audit/2026/p9-evidence/validate_evidence_registry.log`
- `docs/conformance/audit/2026/p9-evidence/validate_evidence_bundles.log`
- `docs/conformance/audit/2026/p9-evidence/pytest_evidence_registry.log`
''',
    }
    for name, content in summaries.items():
        write(dev_gate / name, content)
    write(dev_gate / 'manifest.json', json.dumps({
        'generated_at': CURRENT_DATE,
        'files': sorted(p.name for p in dev_gate.glob('*.md')),
    }, indent=2))

    write(release_gate / 'README.md', '''# Release Gate Results

This directory is the governed gate-results root for release `0.3.17`.

The Phase 9 checkpoint creates the durable structure and snapshot documents required for a stable release bundle. It does **not** claim that Gate D or Gate E are passed for this release line.
''')
    write(release_artifacts / 'README.md', '''# Release Artifacts

This directory is the governed artifacts root for release `0.3.17`.

The Phase 9 checkpoint adds the required durable structure and manifest path. It does **not** claim that the release has a frozen promotion artifact set yet.
''')
    write(release_artifacts / 'artifact-manifest.json', json.dumps({
        'release': RELEASE_VERSION,
        'generated_at': CURRENT_DATE,
        'artifacts': [],
        'note': 'Phase 9 creates the durable release artifact structure but does not claim a promoted Gate E artifact set.',
    }, indent=2))


def build_bundle_docs(registry: dict[str, object]) -> None:
    write(CONFORMANCE / 'EVIDENCE_MODEL.md', f'''# Evidence Model

## Purpose

This document defines the durable evidence model introduced in Phase 9.

The repository now treats certification evidence as a governed product surface rather than an ad hoc collection of audit logs.

## Required lane classes

- unit
- integration
- spec conformance
- security / negative
- docs UI smoke
- CLI smoke
- operator-surface smoke
- server compatibility smoke
- clean-room package tests

## Current governed implementation

The current checkpoint stores:

- a machine-readable claim-to-evidence mapping at `docs/conformance/EVIDENCE_REGISTRY.json`
- a governed dev bundle at `docs/conformance/dev/{DEV_VERSION}/`
- a governed stable-release bundle at `docs/conformance/releases/{RELEASE_VERSION}/`
- lane summaries under the dev bundle `gate-results/` directory
- a release artifact manifest path under the release bundle `artifacts/` directory

## Reproducibility rule

A claim is not Tier 3 certifiable until:

1. the claim row exists in `docs/conformance/CLAIM_REGISTRY.md`
2. the claim row is mapped in `docs/conformance/EVIDENCE_REGISTRY.json`
3. the mapped tests, CI jobs, and artifact paths exist
4. the relevant bundle structure passes validation
5. Gate D and Gate E are passed on the exact chosen build/release

## Current checkpoint status

This Phase 9 checkpoint creates the durable evidence model and validators. It does **not** yet claim Gate D reproducibility or Gate E promotion.
''')

    dev_tests = [
        '- policy/governance validators and tests',
        '- carried-forward spec/docs/security/operator/CLI audit logs from checkpoints 5 through 8',
        '- Phase 9 evidence-registry and bundle validators',
        '- Phase 9 clean-room package build/metadata smoke',
    ]
    write(DEV_ROOT / 'BUILD_NOTES.md', f'''# Build Notes â€” {DEV_VERSION}

## Build identity

- bundle path: `docs/conformance/dev/{DEV_VERSION}/`
- generated for checkpoint date: `{CURRENT_DATE}`
- working tree package version remains `0.3.17`

## Why the dev bundle version differs from package metadata

Phase 9 creates the evidence-lane structure for the next dev-line style checkpoint without claiming that the package metadata has already been advanced or promoted. Version advancement remains part of the later Gate D / Gate E work.

## Evidence sources included in this bundle

{chr(10).join(dev_tests)}

## Current certification position

This bundle establishes durable structure and traceable evidence mapping. It does **not** yet establish Tier 3 certification.
''')

    claims_summary = []
    claim_ids = sorted(registry['claims'])
    for claim_id in claim_ids:
        claims_summary.append(f'- `{claim_id}`')
    write(DEV_ROOT / 'CLAIMS.md', f'''# Claims â€” {DEV_VERSION}

This dev bundle points to the governed claim set for the current cycle.

## Authoritative source

- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/EVIDENCE_REGISTRY.json`

## Claim ids covered by the current dev bundle

{chr(10).join(claims_summary)}
''')

    index_rows = [
        '| Lane | Primary workflow/job | Gate-result summary |',
        '|---|---|---|',
        f'| policy governance | `.github/workflows/policy-governance.yml#validate-policy` | `docs/conformance/dev/{DEV_VERSION}/gate-results/policy-governance.md` |',
        f'| unit | `.github/workflows/evidence-lanes.yml#evidence-lane[unit]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/unit.md` |',
        f'| integration | `.github/workflows/evidence-lanes.yml#evidence-lane[integration]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/integration.md` |',
        f'| spec conformance | `.github/workflows/evidence-lanes.yml#evidence-lane[spec-conformance]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/spec-conformance.md` |',
        f'| security / negative | `.github/workflows/evidence-lanes.yml#evidence-lane[security-negative]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/security-negative.md` |',
        f'| docs UI smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[docs-ui-smoke]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/docs-ui-smoke.md` |',
        f'| CLI smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[cli-smoke]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/cli-smoke.md` |',
        f'| operator-surface smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[operator-surface-smoke]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/operator-surface-smoke.md` |',
        f'| server compatibility smoke | `.github/workflows/evidence-lanes.yml#evidence-lane[server-compat-smoke]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/server-compat-smoke.md` |',
        f'| clean-room package tests | `.github/workflows/evidence-lanes.yml#evidence-lane[clean-room-package]` | `docs/conformance/dev/{DEV_VERSION}/gate-results/clean-room-package.md` |',
    ]
    write(DEV_ROOT / 'EVIDENCE_INDEX.md', f'''# Evidence Index â€” {DEV_VERSION}

## Purpose

This index is the durable entry point for the current dev-bundle evidence lane model.

## Lane index

{chr(10).join(index_rows)}

## Claim mapping source

- `docs/conformance/EVIDENCE_REGISTRY.json`
''')

    write(RELEASE_ROOT / 'RELEASE_NOTES.md', '''Supported claim ids: GOV-010, GATE-007, OAS-001, OAS-006, CLI-001, CLI-002

# Release Notes â€” 0.3.17

Supported claim ids: GOV-010, GATE-007, OAS-001, OAS-006, CLI-001, CLI-002

This governed release bundle is present to establish the durable stable-release evidence structure required by Phase 9.

It records the stable line snapshot for `0.3.17`, but it does **not** claim that Gate D or Gate E have passed for this release line.
''')
    write(RELEASE_ROOT / 'CLAIMS.md', '''Supported claim ids: EVID-003

# Claims â€” 0.3.17

This release bundle points to the governed claim registry and the evidence registry for the stable line snapshot.

## Authoritative sources

- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/EVIDENCE_REGISTRY.json`

## Note

The Phase 9 checkpoint establishes durable release-bundle structure. It does not yet claim a promoted Tier 3 release.
''')
    write(RELEASE_ROOT / 'EVIDENCE_INDEX.md', f'''Supported claim ids: EVID-003

# Evidence Index â€” {RELEASE_VERSION}

## Stable bundle structure

- `RELEASE_NOTES.md`
- `CLAIMS.md`
- `EVIDENCE_INDEX.md`
- `CURRENT_TARGET_SNAPSHOT.md`
- `gate-results/`
- `artifacts/`

## Source dev bundle

- `docs/conformance/dev/{DEV_VERSION}/`

## Claim mapping source

- `docs/conformance/EVIDENCE_REGISTRY.json`
''')
    current_target_text = (CONFORMANCE / 'CURRENT_TARGET.md').read_text(encoding='utf-8')
    write(RELEASE_ROOT / 'CURRENT_TARGET_SNAPSHOT.md', 'Supported claim ids: EVID-003\n\n' + current_target_text)


def main() -> None:
    registry = build_registry()
    write(CONFORMANCE / 'EVIDENCE_REGISTRY.json', json.dumps(registry, indent=2, sort_keys=True))
    build_gate_results_docs()
    build_bundle_docs(registry)


if __name__ == '__main__':
    main()
