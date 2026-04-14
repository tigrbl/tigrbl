# ADR-0023 — Exchange Model

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0006, ADR-0007, ADR-0016, ADR-0024, ADR-0025

## Context

Once the semantic core, protocol binding model, and compiled-plan direction are stable, Tigrbl needs a normalized execution-exchange taxonomy.
The architecture pack already converges on three exchange shapes, but this decision is intentionally placed after the semantic/compiler foundation ADRs.

## Decision

1. Tigrbl execution normalizes onto a closed set of exchange shapes.
2. The exchange set is:
   - `unary`
   - `server_stream`
   - `duplex`
3. Bindings map onto these exchange shapes; the exchange model does not create a second programming model.
4. Kernel compilation may use exchange-specific templates, but semantics remain operation-first and binding-driven.
5. Introducing a new exchange class requires an ADR because it changes core execution taxonomy and plan shape.

## Consequences

- Runtime and compiler logic can share a small set of execution templates.
- New protocol work stays normalized instead of inventing one-off lifecycle categories.
- The exchange model consumes earlier ADRs instead of back-driving them.

## Rejected alternatives

- Per-protocol execution models with no normalization layer.
- Treating every new transport as a new exchange kind.
- Hiding exchange semantics inside transport adapters only.
