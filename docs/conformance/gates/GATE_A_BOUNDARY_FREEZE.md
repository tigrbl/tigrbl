# Gate A: Boundary Freeze

## Objective

Freeze the target boundary, claim language, release-note claim policy, docs pointers, and path-length conformance so scope cannot drift silently during the current cycle.

## Current status

Implemented and refreshed through the Post-promotion handoff checkpoint.

This does **not** mean the boundary changed. It means the boundary-freeze control layer remains enforceable by CI and has been refreshed to keep the frozen current target, the claim registry, and the handoff governance docs synchronized after release promotion.

## Controlled documents for this cycle

The current-target cycle is frozen by these artifacts:

- `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`
- `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`

The frozen boundary documents are:

- `docs/conformance/CURRENT_TARGET.md`
- `docs/governance/TARGET_BOUNDARY.md`

The wider freeze-controlled claim documents are:

- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/governance/CLAIM_TIERS.md`
- `docs/governance/CERTIFICATION_POLICY.md`
- `docs/governance/RELEASE_POLICY.md`

## Automation

Gate A is enforced by:

- `tools/ci/validate_boundary_freeze_manifest.py`
- `tools/ci/enforce_boundary_freeze_diff.py`
- `tools/ci/validate_package_layout.py`
- `tools/ci/validate_doc_pointers.py`
- `tools/ci/validate_root_clutter.py`
- `tools/ci/validate_path_lengths.py`
- `tools/ci/lint_claim_language.py`
- `tools/ci/lint_release_note_claims.py`
- `.github/workflows/policy-governance.yml`

## Change rule

During this cycle, changes to the frozen boundary documents require synchronized updates to:

- `docs/conformance/CLAIM_REGISTRY.md`
- `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
- `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`

If those synchronized updates are missing, CI must fail.

## Exit criteria for this checkpoint line

- scope is frozen for the current-target cycle
- docs and claims cannot drift silently
- stale pointer paths fail mechanically
- unsupported release-note claims fail mechanically
- path-length violations fail mechanically

## Evidence

- `docs/conformance/audit/2026/phase4-boundary-freeze/README.md`
- `docs/conformance/audit/2026/p6-rfc-sec/README.md`
- `docs/conformance/audit/2026/p13-gate-e/README.md`
- `docs/conformance/audit/2026/post-promotion-handoff/README.md`
- `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`
- `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
