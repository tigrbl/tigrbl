# Documentation Map

The authoritative machine-readable source of truth for the repository is `.ssot/registry.json`, with authored ADRs in `.ssot/adr/` and authored specs in `.ssot/specs/`.

`certification/` contains derived certification projections, gate inputs, and historical release bundles. `certification/claims/target.yaml` and `certification/targets/next_target.yaml` are deprecated projection artifacts and must not receive new source edits.

`docs/` remains the authoritative narrative documentation tree. Post-promotion handoff records the post-promotion handoff that freezes stable release `0.3.18` as release history and opens the governed next-target planning line `0.3.19.dev1`.

## Canonical reader path

1. `../.ssot/registry.json`
2. `../.ssot/adr/ADR-1026-certification-truth-model.yaml`
3. `../.ssot/adr/ADR-1033-current-target-boundary.yaml`
4. `../.ssot/adr/ADR-1038-asgi-first-server-agnostic-runtime-strategy.yaml`
5. `../.ssot/adr/ADR-1039-cli-contract-and-server-selection-contract.yaml`
6. `conformance/CURRENT_TARGET.md`
7. `conformance/CURRENT_STATE.md`
8. `conformance/NEXT_STEPS.md`
9. `conformance/NEXT_TARGETS.md`
10. `conformance/RFC_SECURITY_EVIDENCE_MAP.md`
11. `conformance/EVIDENCE_MODEL.md`
12. `conformance/IMPLEMENTATION_MAP.md`
13. `governance/DOC_POINTERS.md`

## Sections

- `governance/` - project rules, claim model, versioning, target boundary, release policy, structure policy, and path-length policy
- `conformance/` - frozen current target, current state, next targets, RFC evidence map, evidence model, implementation map, next steps, claim registry, dev/release bundles, gates, freeze artifacts, and audit evidence
- `.ssot/adr/` - authoritative architectural decisions that govern the current target, the handoff boundary, and next-target work
- `.ssot/specs/` - authoritative normative specs for the SSOT model and repo-governed contracts
- `developer/` - operator surfaces, operator reference pages, the implemented CLI surface, the certification lane model, package inventory, and CI validation guidance
- `release-notes/` - governed release-note entry point and release-note claim policy examples
- `notes/` - work-in-progress and archived notes
- `conformance/archive/` - archived legacy status/build proof materials retained for traceability
