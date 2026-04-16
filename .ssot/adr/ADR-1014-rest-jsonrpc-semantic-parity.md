# ADR-0014 â€” REST and JSON-RPC Semantic Parity

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0001, ADR-0006, ADR-0007, ADR-0013, ADR-0015, ADR-0016

## Context

REST and JSON-RPC are distinct transport/binding surfaces, but Tigrbl should not let them drift into different semantic frameworks.
The architecture pack repeatedly treats them as different projections over the same semantic operations.

## Decision

1. REST and JSON-RPC project the same semantic operation model.
2. Canonical operations available through REST must be representable through JSON-RPC where the semantic contract applies, and vice versa.
3. Differences between the two surfaces are limited to:
   - envelope/framing;
   - transport-facing method/route selection;
   - protocol-native response/error shapes;
   - protocol-native metadata.
4. Semantic differences such as authorization rules, canonical operation behavior, and engine effects may not diverge by binding.
5. Tests and docs must evaluate parity at the semantic layer, not only at the transport layer.

## Consequences

- Framework behavior remains horizontal across the two most important unary bindings.
- JSON-RPC stops becoming a second-class or semantically divergent transport.
- Canonical ops and engines need only one semantic definition.
- Later parity/certification work gets a measurable target.

## Rejected alternatives

- Binding-specific semantics for the same canonical operation.
- Treating JSON-RPC as a custom-op-only surface.
- Duplicating operation semantics into REST-specific and RPC-specific implementations.

