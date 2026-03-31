# Contributing to Tigrbl

## Source of truth

The authoritative documentation tree is `docs/`. Before changing code, confirm the target boundary and current state in:

- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`

## Contribution expectations

Contributions should:

- preserve the current target boundary unless the boundary docs and ADRs are updated intentionally
- avoid introducing certification language that exceeds the documented claim tier
- keep repo-level documentation under `docs/` instead of adding new root-level notes
- keep package structure consistent with `docs/governance/PACKAGE_STRUCTURE_POLICY.md`
- add or update tests when a public surface changes
- update conformance and developer docs when behavior or claims change

## Branch and pull request hygiene

Each change should:

1. describe the affected surface area
2. state whether the change is in-boundary, deferred, or out-of-boundary
3. identify any required docs changes
4. identify any test or evidence updates
5. avoid unrelated root-level clutter or generated build output

## Documentation rules

- new governance, target, state, release, and certification docs belong under `docs/`
- work-in-progress notes belong under `docs/notes/wip/YYYY/`
- resolved notes belong under `docs/notes/archive/YYYY/`
- do not add loose Markdown scratch files at the repository root

## Testing expectations

At a minimum, run the test lanes that cover the surface you changed. The existing checkpoint evidence shows Rust workspace tests and selected Python native-surface tests; see `docs/developer/TESTING_GUIDE.md` and the archived validation materials for the current baseline.

## Security issues

Do not file public issues for exploitable vulnerabilities. Follow `SECURITY.md`.
