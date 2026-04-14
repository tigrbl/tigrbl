# ADR-0022 — Tigrcorn / Uvicorn / Hypercorn Interop and Conformance

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0005, ADR-0007, ADR-0020, ADR-0021, ADR-0023, ADR-0024, ADR-0025

## Context

Tigrbl is intended to remain ASGI-portable, but portability must be made concrete.
Interop belongs after the semantic, spec, binding, and compilation foundation is frozen, because server differences should be evaluated against a stable boundary.

## Decision

1. Tigrbl targets conformance across Tigrcorn, Uvicorn, and Hypercorn at the preserved ASGI boundary.
2. Server interop is judged relative to:
   - ASGI boundary behavior;
   - required scope/event surfaces for supported bindings;
   - documented extension expectations where ASGI has no native surface.
3. Server-specific optimizations may exist, but they may not redefine the core semantic framework contract.
4. Interop status is evidence-based and test-lane-backed.
5. Where a protocol surface depends on server extensions, that dependency must be documented explicitly rather than implied as universal ASGI behavior.

## Consequences

- Server portability becomes measurable.
- Tigrbl core semantics stay decoupled from one server implementation.
- Extension surfaces such as WebTransport stay honest about portability constraints.
- Later certification can distinguish portable and server-specific claims cleanly.

## Rejected alternatives

- Assuming all ASGI servers are behaviorally identical.
- Baking Tigrcorn-specific semantics into core Tigrbl behavior.
- Implying interop for extension surfaces with no evidence.
