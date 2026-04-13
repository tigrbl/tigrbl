# Testing Guide

## Required lane classes for the current certification program

The governed evidence model now uses these lane classes:

- unit
- integration
- spec conformance
- security / negative
- docs UI smoke
- CLI smoke
- operator-surface smoke
- server compatibility smoke
- clean-room package tests
- promotion and release

## Current workflow entry points

- `.github/workflows/policy-governance.yml`
- `.github/workflows/operator-surface.yml`
- `.github/workflows/cli-smoke.yml`
- `.github/workflows/evidence-lanes.yml`
- `.github/workflows/gate-b-surface-closure.yml`
- `.github/workflows/gate-c-conformance-security.yml`
- `.github/workflows/gate-d-reproducibility.yml`
- `.github/workflows/gate-e-promotion.yml`

## Current governed validators

- `tools/ci/validate_package_layout.py`
- `tools/ci/validate_doc_pointers.py`
- `tools/ci/validate_root_clutter.py`
- `tools/ci/validate_path_lengths.py`
- `tools/ci/lint_claim_language.py`
- `tools/ci/validate_boundary_freeze_manifest.py`
- `tools/ci/lint_release_note_claims.py`
- `tools/ci/validate_evidence_registry.py`
- `tools/ci/validate_evidence_bundles.py`
- `tools/ci/validate_gate_b_surface_closure.py`
- `tools/ci/validate_gate_c_conformance_security.py`
- `tools/ci/validate_gate_d_reproducibility.py`
- `tools/ci/validate_gate_e_promotion.py`

## Current bundle entry points

- `docs/conformance/dev/0.3.18.dev1/EVIDENCE_INDEX.md`
- `docs/conformance/releases/0.3.18/EVIDENCE_INDEX.md`

## Contributor guidance

When changing any current-target surface:

1. run the affected unit/integration/spec/security/operator/CLI/promotion lanes as appropriate
2. refresh any affected governed docs
3. refresh the evidence registry if a claim row, workflow, or artifact path changes
4. keep the dev/release bundle structures valid
5. refresh the Gate A manifest if frozen boundary docs change
