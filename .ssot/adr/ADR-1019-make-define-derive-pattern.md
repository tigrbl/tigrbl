# ADR-1019: ADR-0019 — Make / Define / Derive Pattern

# ADR-0019 — Make / Define / Derive Pattern

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0003, ADR-0004, ADR-0016, ADR-0017, ADR-0018, ADR-0020

## Context

The repo needs a reusable design pattern for moving from user-authored inputs to canonical framework objects and then to projections such as docs, bindings, plans, and runtime behavior.
Without a stable pattern, each subsystem invents its own normalization pipeline.

## Decision

1. Tigrbl adopts the pattern:
   - **make**: collect or construct raw declarative inputs;
   - **define**: normalize them into canonical authoritative objects;
   - **derive**: compute projections from canonical objects.
2. Derivation must happen from canonical forms, not directly from raw user input.
3. Public APIs should expose where they are in this pipeline.
4. Canonical specs, binding projections, docs outputs, and compiled kernel plans are all derived artifacts.
5. This pattern applies across Python and Rust implementations and across docs/tooling layers.
6. Shortcuts and decorators live in the make layer; semantics live in define; plans/docs/runtime projections live in derive.

## Consequences

- Design becomes more uniform across packages.
- Debugging and tooling improve because every stage has a clear responsibility.
- Merge precedence and canonicalization happen in one place.
- Future parity work has a cleaner set of artifacts to compare.

## Rejected alternatives

- Directly deriving plans, docs, or runtime behavior from raw decorator arguments.
- Blurring canonical definition and projection layers.
- Allowing each package to invent its own input-normalization pipeline.
