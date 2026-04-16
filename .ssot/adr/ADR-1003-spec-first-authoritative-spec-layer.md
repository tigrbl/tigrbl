# ADR-0003 â€” Spec-First Authoritative Spec Layer

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0001, ADR-0004, ADR-0006, ADR-0007, ADR-0016, ADR-0017, ADR-0018, ADR-0019

## Context

Tigrbl needs a single authoritative declarative layer so that execution, docs, hooks, and compilation are all driven from the same canonical objects.
The architecture pack consistently places this responsibility in `tigrbl_core._spec`, with `tigrbl_spec` acting as a facade or re-export layer rather than as a second source of truth.

## Decision

1. `tigrbl_core._spec` is the authoritative declarative layer for public semantic and binding definitions.
2. `tigrbl_spec` may re-export, compose, or facade the authoritative definitions, but it may not redefine their semantics.
3. Public framework behavior must be expressible through canonical spec objects before it is considered supported.
4. Decorators, aliases, and convenience APIs must expand into canonical specs rather than creating parallel declarative pathways.
5. Docs generation, compatibility reporting, and kernel compilation must consume the same canonical specs.
6. Execution behavior that is not representable in spec is not claimable as a public framework feature.

## Consequences

- Public behavior becomes inspectable, serializable, and compilable.
- Docs drift is reduced because docs and execution derive from the same declarations.
- Later ADRs on merge precedence, decorators, and plan compilation all get a stable foundation.
- Internal shortcuts that cannot be represented in spec are forced either to become real spec features or to remain internal-only.

## Rejected alternatives

- Runtime-first public behavior.
- Docs-first declarations disconnected from execution.
- Multiple authoritative spec layers with informal reconciliation.

