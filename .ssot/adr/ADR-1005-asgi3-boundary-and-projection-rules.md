# ADR-0005 â€” ASGI3 Boundary and Projection Rules

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0006, ADR-0007, ADR-0016, ADR-0022, ADR-0023, ADR-0024, ADR-0025

## Context

Tigrbl sits behind an ASGI-shaped server boundary. The architecture pack is explicit that richer semantics must be projected above `scope`, `receive`, and `send`, not by inventing a new server/app contract.
This decision is foundational because protocol support, server interop, and runtime normalization all depend on it.

## Decision

1. The server/framework boundary remains ASGI3-shaped: `async def app(scope, receive, send)`.
2. Tigrbl does not replace the server contract with a custom non-ASGI boundary.
3. Standard ASGI `scope.type` values remain authoritative where they exist (`http`, `websocket`, `lifespan`), with explicit extension types allowed only where ASGI has no standard surface.
4. Richer semantics are projected above the boundary through:
   - scope extensions;
   - binding metadata;
   - receive/send event interpretation;
   - compiled/runtime classification.
5. Transport-specific projection logic belongs in concrete/runtime layers, not in the semantic operation model.
6. Server interop with Tigrcorn, Uvicorn, and Hypercorn must be evaluated relative to this preserved boundary.

## Consequences

- Tigrbl remains server-portable instead of server-owned.
- The protocol model can grow without changing the external server contract.
- Later runtime taxonomies may refine execution semantics without destabilizing server integration.
- Concrete transport code remains an adapter layer rather than a second framework kernel.

## Rejected alternatives

- Replacing ASGI with a framework-specific boundary.
- Encoding all richer semantics into custom server APIs.
- Making Tigrbl depend on one server's internal request/response objects.

