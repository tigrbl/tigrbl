# ADR-0025 â€” OpChannel and Runtime IO Abstraction

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0002, ADR-0005, ADR-0016, ADR-0020, ADR-0022, ADR-0023, ADR-0024

## Context

Once the runtime taxonomy is normalized, Tigrbl needs a runtime-owned transport abstraction so handlers and execution loops can remain transport-neutral where possible.
The architecture pack places this abstraction at the typing/ports boundary and keeps implementations runtime-owned.

## Decision

1. Tigrbl defines a transport-neutral runtime channel abstraction for live transport interaction.
2. The public protocol/trait lives at the typing/ports boundary; concrete implementations live in runtime packages/crates.
3. The channel abstraction is runtime-owned, not declarative-spec-owned and not concrete-adapter-owned.
4. Channel capabilities are transport-dependent, but the abstraction remains one normalized surface.
5. The channel abstraction is used only where live transport interaction is required; it does not replace the semantic operation model or the binding model.
6. Concrete transport adapters feed the runtime abstraction; they do not bypass runtime-owned execution control.

## Consequences

- Live transport execution gains a normalized abstraction point.
- Runtime/concrete coupling is reduced rather than deepened.
- Later transport growth can extend runtime adapters without redefining semantic authoring.
- Python/Rust parity has a clear location for mirrored IO abstractions.

## Rejected alternatives

- Separate public channel abstractions per transport.
- Putting the channel abstraction in spec or concrete layers.
- Letting transport adapters invoke handlers directly without a runtime-owned abstraction.

