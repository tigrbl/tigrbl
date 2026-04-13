# Versioning Policy

## Current rule set

- development checkpoints use `0.x.y.devN`
- stable releases use `0.x.y`
- release candidates are not used in the current program

## Promotion rule

A dev build is promoted to stable only after the promotion gate passes on the exact chosen build.

## Current release implication

The exact chosen dev build `0.3.18.dev1` is promoted to stable release `0.3.18` in the governed release bundle.

## Phase 14 continuation rule

Post-promotion handoff has now opened the next governed development line as `0.3.19.dev1`.

The patch continuation line was chosen because this checkpoint only performs release-history freeze and next-target planning isolation. It does **not** itself introduce a promoted new feature release.

The active `0.3.19.dev1` line may not use certification wording unless a later governed cycle closes and proves its own claims.
