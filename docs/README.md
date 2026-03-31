# Documentation Map

This is the single authoritative documentation tree for the repository.

## Canonical reader path

1. [`conformance/CURRENT_TARGET.md`](conformance/CURRENT_TARGET.md)
2. [`conformance/CURRENT_STATE.md`](conformance/CURRENT_STATE.md)
3. [`conformance/NEXT_STEPS.md`](conformance/NEXT_STEPS.md)
4. [`governance/DOC_POINTERS.md`](governance/DOC_POINTERS.md)

## Sections

- `governance/` — project rules, claim model, versioning, target boundary, structure policy
- `conformance/` — current target, current state, next steps, claim registry, gates
- `adr/` — architectural decisions that govern the current target and future work
- `developer/` — operator surfaces, CLI contract, testing guidance, developer-oriented references
- `notes/` — work-in-progress and archived notes
- `conformance/archive/` — archived legacy status/build proof materials retained for traceability

## Legacy developer docs already in tree

The supplied archive already included developer-oriented material under:

- `docs/architecture/`
- `docs/migration/`
- `docs/testing/`

Those paths are still inside the authoritative docs tree. Future general-purpose developer docs should prefer `docs/developer/` unless there is a strong reason to keep a specialized section.
