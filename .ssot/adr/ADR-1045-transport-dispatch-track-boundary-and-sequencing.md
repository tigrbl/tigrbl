# ADR-1045 - Transport-Dispatch Track Boundary and Sequencing

- **Status:** Accepted
- **Date:** 2026-04-18
- **Related ADRs:** ADR-1006, ADR-1014, ADR-1016, ADR-1024, ADR-1025, ADR-1044

## Context

The active `0.3.19.dev1` line already carries the datatype/table next-target program. The transport-dispatch repair work is a separate architectural effort that changes dispatch ownership, transport binding materialization, and JSON-RPC ingress identity. It needs its own governed track, its own boundary snapshot, and its own sequencing before code delivery starts.

## Decision

1. The transport-dispatch repair work is a distinct next-target track inside the active `0.3.19.dev1` line.
2. The track must create and link its ADRs, specs, features, tests, and claims before implementation work starts.
3. The track must create a dedicated SSOT boundary, attach its transport-dispatch features to that boundary, and freeze it before delivery work begins.
4. The frozen `0.3.18` current-boundary release history remains unchanged; this track governs only the active next-target line.
5. The repo-local `ssot-registry` tool version used to author the track is recorded as part of the track setup evidence.

## Consequences

- transport-dispatch work becomes a governed next-target program slice instead of an untracked implementation branch
- the active line can sequence transport-dispatch work independently from datatype/table work while still sharing the same dev version
- implementation can start only after the boundary, links, and freeze artifacts exist

## Rejected alternatives

- folding transport-dispatch changes into the frozen `0.3.18` release boundary
- starting code delivery before the track has ADR/SPEC/feature/test/claim coverage
- reusing the existing default SSOT boundary without a dedicated transport-dispatch freeze snapshot
