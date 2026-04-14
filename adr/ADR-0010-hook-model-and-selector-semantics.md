# ADR-0010 — Hook Model and Selector Semantics

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0004, ADR-0008, ADR-0009, ADR-0011, ADR-0012, ADR-0017, ADR-0018, ADR-0023, ADR-0024

## Context

Hooks are part of the framework contract, not a best-effort extension point. They need deterministic attachment, ordering, and scope rules.
The current architecture requires phase-bound hookability and leaves room for later classifier extensions.

## Decision

1. Hooks attach only to declared legal phases.
2. Hook selection is deterministic and phase-bound.
3. The required selector surface for the foundation layer is:
   - operation identity or operation class;
   - phase;
   - binding where relevant.
4. The hook system reserves extension points for later execution classifiers without reopening the basic hook model.
5. Hook execution ordering is stable and explicit:
   - by precedence class;
   - then by declaration order within class.
6. Hooks may observe and transform only the state legal for their phase.
7. Hooks may not bypass guards, dependency ordering, or transaction ownership.

## Consequences

- Hooks become composable instead of surprising.
- Future classifier-rich hook selection can extend the model rather than replace it.
- Phase legality and merge precedence can reason about hook behavior.
- Docs and tests can enumerate hook surfaces cleanly.

## Rejected alternatives

- Free-form middleware-style hooks with no phase constraints.
- Transport-specific hook systems.
- Implicit ordering driven by import order or container iteration order.
