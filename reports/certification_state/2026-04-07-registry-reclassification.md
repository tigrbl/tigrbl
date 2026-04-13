# Certification State Report

Date: 2026-04-07

## Registry reclassification

The repository certification bundle is now reclassified into four explicit authority files:

- `certification/claims/current.yaml`
- `certification/claims/target.yaml`
- `certification/claims/blocked.yaml`
- `certification/claims/evidenced.yaml`

## Interpretation

- `current` is the frozen `0.3.18` boundary and the controls that remain in force now.
- `target` is the governed `0.3.19.dev1` datatype/table program.
- `blocked` is the set of known non-certifiable dev-line facts and promotion blockers.
- `evidenced` is the set of claims and gates backed directly by release-bundle evidence.

## Package checkpoint statement

This repository checkpoint is complete for Phase 0 boundary freeze and truth-model work.

The authority tree is now machine-validated through `tools/ci/validate_certification_tree.py`.

The checkpoint package is not a statement that the active line `0.3.19.dev1` is fully featured or fully RFC compliant.

The checkpoint package is a statement that the repository now records those facts explicitly, fail-closed, and machine-validated.
