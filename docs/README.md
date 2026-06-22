# Documentation Map

The authoritative source of truth for governed repository state is `.ssot/registry.json`, with authored ADRs in `.ssot/adr/` and authored specs in `.ssot/specs/`.

`.ssot/projections/certification/` contains derived certification projections, gate inputs, and historical release bundles. `.ssot/projections/certification/claims/target.yaml` and `.ssot/projections/certification/targets/next_target.yaml` are deprecated projection artifacts and must not receive new source edits.

`docs/` is a non-authoritative narrative, evidence, release-bundle, and operator projection layer over SSOT state. Post-promotion handoff records the post-promotion handoff that freezes stable release `0.3.18` as release history and opens the governed next-target planning line `0.3.19.dev1`.

`tools/ci/` is a non-authoritative validation and fail-closed guardrail layer. CI scripts check that projections match SSOT-backed state, but they do not define claims, features, gates, boundaries, releases, ADRs, or specs.

## Canonical reader path

1. `../.ssot/registry.json`
2. `../.ssot/adr/ADR-1026-certification-truth-model.yaml`
3. `../.ssot/adr/ADR-1033-current-target-boundary.yaml`
4. `../.ssot/adr/ADR-1038-asgi-first-server-agnostic-runtime-strategy.yaml`
5. `../.ssot/adr/ADR-1039-cli-contract-and-server-selection-contract.yaml`
6. `../.ssot/adr/ADR-1060-docs-ci-non-authoritative-projections.yaml`
7. `../.ssot/specs/SPEC-1002-docs-ci-projection-authority-contract.yaml`
8. `conformance/README.md`
9. `conformance/CURRENT_TARGET.md`
10. `developer/AUTHORING_BCP.md`
11. `developer/TRANSPORTS_AND_FRAMING.md`
12. `governance/DOC_POINTERS.md`

## Sections

- `governance/` - non-authoritative narrative projections of project rules, claim model, versioning, target boundary, release policy, structure policy, and path-length policy
- `conformance/` - non-authoritative narrative and evidence projections for the frozen current target, dev/release bundles, gates, release history, archived legacy material, and audit/checkpoint evidence
- `.ssot/adr/` - authoritative architectural decisions that govern the current target, the handoff boundary, and next-target work
- `.ssot/specs/` - authoritative normative specs for the SSOT model and repo-governed contracts
- `developer/` - non-authoritative operator and developer guidance for authoring BCPs, transport and framing support, operator surfaces, operator reference pages, the implemented CLI surface, the certification lane model, package inventory, and CI validation guidance
- `release-notes/` - governed release-note entry point and release-note claim policy examples
- `notes/` - work-in-progress and archived notes
- `conformance/archive/` - archived legacy status/build proof materials retained for traceability
