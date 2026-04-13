# CI Validation

The current certification program uses policy validators, evidence-lane workflows, gate-specific validators/workflows, and a dedicated post-promotion handoff validator.

## Validation scripts

- `tools/ci/validate_package_layout.py`
- `tools/ci/validate_doc_pointers.py`
- `tools/ci/validate_root_clutter.py`
- `tools/ci/validate_path_lengths.py`
- `tools/ci/lint_claim_language.py`
- `tools/ci/validate_boundary_freeze_manifest.py`
- `tools/ci/enforce_boundary_freeze_diff.py`
- `tools/ci/lint_release_note_claims.py`
- `tools/ci/validate_evidence_registry.py`
- `tools/ci/validate_evidence_bundles.py`
- `tools/ci/validate_certification_tree.py`
- `tools/ci/validate_phase1_declared_surface.py`
- `tools/ci/validate_phase4_native_parity.py`
- `tools/ci/validate_phase5_tigrcorn_operator_surface.py`
- `tools/ci/validate_phase6_tigrcorn_hardening.py`
- `tools/ci/validate_phase7_claim_lifecycle.py`
- `tools/ci/validate_gate_b_surface_closure.py`
- `tools/ci/validate_gate_c_conformance_security.py`
- `tools/ci/validate_gate_d_reproducibility.py`
- `tools/ci/validate_gate_e_promotion.py`
- `tools/ci/validate_phase14_handoff.py`
- `tools/ci/generate_boundary_freeze_manifest.py`

## What is enforced

- package layout matches the normalized workspace policy
- package-local Markdown does not bypass the governed docs tree
- required pointer documents exist and resolve to live files or directories
- root clutter and generated artifact directories are rejected
- file names, directory names, and repository-relative paths stay within the governed limits
- claim wording outside governance/conformance records does not overstate current release status
- the Gate A freeze manifest matches the current frozen boundary and claim-control documents
- boundary-doc changes cannot land without synchronized claim-registry and freeze-artifact updates
- release-note files must declare governed claim IDs
- every claim row maps to tests, CI jobs, and artifact paths in `docs/conformance/EVIDENCE_REGISTRY.json`
- dev/release bundle structures contain the required governed files and directories
- the certification authority tree keeps the four-state truth model and Phase 0 exit criteria machine-checked
- the Phase 1 declared-surface checkpoint stays documented and synchronized with the policy workflow
- native backend claim language remains fail-closed until the Phase 4 parity checkpoint is documented and wired in CI
- the Phase 5 Tigrcorn operator surface stays documented, example-backed, and fail-closed for interop/benchmark certification claims
- the Phase 6 Tigrcorn hardening package stays documented, profile-backed, and fail-closed for negative-certification claims
- the Phase 7 claim lifecycle and release certification-bundle artifacts stay synchronized and machine-checked
- Gate E promotion output stays synchronized to the exact chosen dev build and the promoted stable release bundle
- the Phase 14 handoff keeps frozen release history separated from the active next-line bundle

## Workflows

### Policy governance

The workflow at `.github/workflows/policy-governance.yml` runs the validation suite on push, pull request, and manual dispatch.

### Operator surface

The workflow at `.github/workflows/operator-surface.yml` runs the Phase 7 operator-surface closure tests and docs parity checks.

### CLI smoke

The workflow at `.github/workflows/cli-smoke.yml` runs the Phase 8 CLI command smoke tests and the supported-server compatibility smoke tests.

### Evidence lanes

The workflow at `.github/workflows/evidence-lanes.yml` runs the current certification lane classes:

- unit
- integration
- spec conformance
- security / negative
- docs UI smoke
- CLI smoke
- operator-surface smoke
- server compatibility smoke
- clean-room package tests

### Gate B surface closure

The workflow at `.github/workflows/gate-b-surface-closure.yml` reruns the docs UI, operator-surface, and CLI proof slices together and applies `tools/ci/validate_gate_b_surface_closure.py`.

### Gate C conformance/security

The workflow at `.github/workflows/gate-c-conformance-security.yml` reruns the retained spec/security proof slice and applies `tools/ci/validate_gate_c_conformance_security.py`.

### Gate D reproducibility

The workflow at `.github/workflows/gate-d-reproducibility.yml` reruns the clean-room package and installed-package proof slice and applies `tools/ci/validate_gate_d_reproducibility.py`.

### Gate E promotion

The workflow at `.github/workflows/gate-e-promotion.yml` validates the promoted stable release bundle and frozen stable documentation pointers via `tools/ci/validate_gate_e_promotion.py`.

### Phase 14 post-promotion handoff

The workflow at `.github/workflows/phase14-post-promotion-handoff.yml` validates the handoff boundary, active next-line versioning, next-target planning docs, and archived WIP state via `tools/ci/validate_phase14_handoff.py`.
