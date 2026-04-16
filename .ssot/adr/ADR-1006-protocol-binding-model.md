# ADR-0006 â€” Protocol Binding Model

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0001, ADR-0003, ADR-0005, ADR-0007, ADR-0014, ADR-0016, ADR-0018, ADR-0023

## Context

Transport support in Tigrbl must scale horizontally. The architecture pack already normalizes REST, RPC, streaming, websocket, and WebTransport as bindings over the same semantic model.
This ADR freezes the separation between semantics and exposure.

## Decision

1. A binding declares how a semantic operation is exposed over a transport/protocol surface.
2. Bindings do not redefine operation semantics; they project them.
3. Binding responsibility includes:
   - transport/protocol identifier;
   - path/method or equivalent selector surface;
   - framing information where applicable;
   - transport-specific metadata required for docs and execution;
   - capability constraints relevant to compilation/execution.
4. Semantic responsibility remains in the operation model, canonical operation definitions, and hooks/guards.
5. Docs generation is binding-driven: transport-facing artifacts are projections from bindings over semantic operations.
6. Any new protocol must enter through a binding specification, not a parallel route subsystem.

## Consequences

- Protocol growth stays additive instead of fragmenting the framework.
- Docs, compilation, and execution all share the same binding vocabulary.
- Semantic parity across bindings becomes measurable.
- Binding specs become a first-class planning surface for kernel compilation and server interop.

## Rejected alternatives

- Separate route subsystems per protocol.
- Protocol-specific handler decorators with unique semantics.
- Treating bindings as runtime-only details with no spec representation.

