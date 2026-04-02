# Phase 6 RFC Security and Path-Length Audit Evidence

This directory records the evidence captured for the Phase 6 checkpoint.

## Checkpoint scope

This phase did two things:

- closed the retained exact RFC auth rows at the framework boundary (`7235`, `7617`, `6750`)
- declared, validated, and corrected repository name/path-length conformance

It did **not** close the remaining docs-UI, operator-surface, or unified CLI rows.

## Boundary freeze refresh

The Gate A freeze artifacts were refreshed after the intentional Phase 6 boundary narrowing.

- marker: `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`
- manifest: `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
- cycle id: `current-target-cycle-2026-phase6`
- freeze tag equivalent: `phase6-boundary-refresh-2026-03-31`
- manifest sha256: `9fe82ecb944019969068efe2ae703512d6c75056c1f2d3f209c5fcc520ec8dcf`

## Policy validator results on the final clean tree

- `validate_package_layout.py` — passed
- `validate_doc_pointers.py` — passed
- `validate_root_clutter.py` — passed
- `validate_path_lengths.py` — passed
- `lint_claim_language.py` — passed
- `validate_boundary_freeze_manifest.py` — passed
- `lint_release_note_claims.py` — passed (`no release notes present`)

## Pytest results on the standalone Phase 6 suite

- `test_governance_validators.py` — 1 passed
- `test_path_length_policy.py` — 1 passed
- `test_http_auth_challenges.py` — 7 passed
- total Phase 6 standalone pytest slice — 9 passed

## Path-length conformance summary

- declared max file name length: `64`
- declared max directory name length: `48`
- declared max repository-relative path length: `160`
- observed max file name length: `55`
- observed max directory name length: `45`
- observed max repository-relative path length: `154`

## Evidence files

- `validate_package_layout.log`
- `validate_doc_pointers.log`
- `validate_root_clutter.log`
- `validate_path_lengths.log`
- `lint_claim_language.log`
- `validate_boundary_freeze_manifest.log`
- `lint_release_note_claims.log`
- `test_governance_validators.log`
- `test_path_length_policy.log`
- `test_http_auth_challenges.log`
