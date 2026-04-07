# Documentation Map

The root `certification/` tree is the authoritative certification boundary and truth model for the repository.

`docs/` remains the authoritative narrative documentation tree. Phase 14 records the post-promotion handoff that freezes stable release `0.3.18` as release history and opens the governed next-target planning line `0.3.19.dev1`.

## Canonical reader path

1. `../certification/boundary.yaml`
2. `../reports/current_state/2026-04-07-phase0-certification-freeze.md`
3. `../reports/certification_state/2026-04-07-registry-reclassification.md`
4. `conformance/CURRENT_TARGET.md`
5. `conformance/CURRENT_STATE.md`
6. `conformance/NEXT_TARGETS.md`
7. `conformance/RFC_SECURITY_EVIDENCE_MAP.md`
8. `conformance/EVIDENCE_MODEL.md`
9. `conformance/IMPLEMENTATION_MAP.md`
10. `governance/DOC_POINTERS.md`

## Sections

- `governance/` — project rules, claim model, versioning, target boundary, release policy, structure policy, and path-length policy
- `conformance/` — frozen current target, current state, next targets, RFC evidence map, evidence model, implementation map, next steps, claim registry, dev/release bundles, gates, freeze artifacts, and audit evidence
- `adr/` — architectural decisions that govern the current target, the handoff boundary, and next-target work
- `developer/` — operator surfaces, operator reference pages, the implemented CLI surface, the certification lane model, package inventory, and CI validation guidance
- `release-notes/` — governed release-note entry point and release-note claim policy examples
- `notes/` — work-in-progress and archived notes
- `conformance/archive/` — archived legacy status/build proof materials retained for traceability
