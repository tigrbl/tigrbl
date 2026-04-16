# ADR-0001 â€” One Semantic Op Model

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0006, ADR-0007, ADR-0014, ADR-0023, ADR-0024, ADR-0025

## Context

Tigrbl needs a stable semantic center before it can support more transports, more runtimes, and more optimization work. 
The architecture pack already converges on one semantic operation model with bindings layered over it, rather than transport-specific programming models. 
Without an explicit decision here, websocket, streaming, and RPC surfaces tend to grow separate handler styles, separate middleware paths, and separate lifecycle semantics.

## Decision

1. The semantic unit of composition in Tigrbl is the operation declared through the canonical operation-definition surface.
2. All transport surfaces are projections of that same semantic operation model.
3. No binding may introduce a separate authoring model, separate handler contract, or separate lifecycle contract that bypasses the semantic operation model.
4. Canonical operations, custom operations, hooks, docs projection, and kernel compilation all start from the same semantic operation definition.
5. Transport-specific concerns belong to bindings, runtime execution, and docs projection, not to the semantic definition itself.

## Consequences

- Tigrbl gets one source of truth for behavior, docs, hooks, guards, and compilation.
- REST, JSON-RPC, streaming, websocket, and future transports remain horizontally aligned.
- New protocols are added by extending bindings and runtime execution rather than by creating another framework inside the framework.
- This ADR becomes a prerequisite for binding parity, kernel compilation, and interop ADRs.

## Rejected alternatives

- Separate websocket and SSE programming models.
- Transport-owned handler contracts.
- Route-type-specific semantics that are not expressible through the canonical operation model.

