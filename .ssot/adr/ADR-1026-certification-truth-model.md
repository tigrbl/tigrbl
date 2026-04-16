# ADR-0001 Certification Truth Model

## Status

Accepted.

## Decision

The repository adopts `certification/` as the authoritative certification boundary and truth model.

The authoritative classification states are:

- `current`
- `target`
- `blocked`
- `evidenced`

Narrative certification prose under `docs/` is subordinate to this root-owned authority tree.

## Rationale

The existing registry and conformance documents provide strong traceability, but they intentionally mix frozen release claims, next-target plans, deferred work, and evidence scaffolding. That is useful for readers but insufficient as a fail-closed release-control model.

## Consequences

- certification wording can be checked against a single root authority tree
- next-target planning is recorded without silently inheriting release-grade language
- Phase 0 exit criteria become machine-readable and auditable

