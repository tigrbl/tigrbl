# ADR-1012: ADR-0012 — DB Guards and Transaction Guardrails

# ADR-0012 — DB Guards and Transaction Guardrails

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0008, ADR-0009, ADR-0011, ADR-0013, ADR-0015, ADR-0016

## Context

Canonical operations depend on database and engine access, but unrestricted engine access inside arbitrary code paths leads to ownership leaks, hidden transaction semantics, and plan/runtime mismatch.
The repo already has DB- and tx-oriented system atoms; this ADR freezes the guardrail model.

## Decision

1. Database and engine access for canonical operations is mediated by framework-owned guards and transaction control points.
2. Transaction ownership belongs to the compiled/runtime lifecycle, not to ad hoc handler code.
3. Guard rules distinguish read-only and mutating work.
4. Canonical mutating operations may not execute outside legal transaction/guard paths.
5. Engine handles exposed to user code, if any, are capability-bounded and may not carry implicit commit/rollback authority.
6. Cross-engine behavior must be explicit and capability-declared; it may not be smuggled through default OLTP paths.
7. Guard failures fail closed before persistence side effects occur.

## Consequences

- Canonical ops keep predictable tx behavior.
- Engine interoperability remains explicit instead of accidental.
- The compiler can reason about tx ownership and barriers.
- User extensions have clearer boundaries around persistence semantics.

## Rejected alternatives

- Letting arbitrary handlers manage framework-owned transactions implicitly.
- Exposing raw database state to all handlers by default.
- Hiding cross-engine fan-in inside canonical OLTP behavior.
