# Build Notes — 0.3.18.dev1

## Build identity

- bundle path: `docs/conformance/dev/0.3.18.dev1/`
- generated for checkpoint date: `2026-04-01`
- working tree package version is now `0.3.18.dev1`

## Why the dev bundle version differs from package metadata

Phase 12 synchronizes the facade package metadata to the selected candidate build and records the clean-room package and installed-package smoke manifests against the same governed dev bundle.

## Evidence sources included in this bundle

- policy/governance validators and tests
- carried-forward spec/docs/security/operator/CLI audit logs from checkpoints 5 through 9
- Phase 10 Gate B validator, workflow, and audit logs
- current dev-bundle gate-results summaries
- Gate D clean-room package and installed-package smoke manifests

## Current certification position

This bundle proves Gates B, C, and D at checkpoint quality on the selected candidate build. It is the exact governed dev bundle later promoted in Phase 13 to stable release `0.3.18`.


## Promotion note

This exact dev bundle is the governed source bundle promoted to stable release `0.3.18` in Phase 13.
