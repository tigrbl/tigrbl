# ADR-0011 â€” Security Deps and Deps Ordering

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0004, ADR-0009, ADR-0010, ADR-0012, ADR-0016

## Context

The architecture pack treats security dependencies as a distinct class that must execute before ordinary dependencies.
This invariant is important enough to deserve an explicit ADR because it affects correctness, safety, and generated plan shape.

## Decision

1. Tigrbl distinguishes `security_deps` from ordinary `deps`.
2. `security_deps` always execute before ordinary `deps`.
3. Failure in `security_deps` fails closed and prevents ordinary dependency resolution and handler execution.
4. This ordering is invariant across bindings and operations.
5. Merge rules for `security_deps` and `deps` must preserve category separation while allowing deterministic concatenation and de-duplication.
6. Compiler and runtime paths may not collapse `security_deps` and `deps` into one undifferentiated list.

## Consequences

- Security-sensitive checks cannot be accidentally pushed behind ordinary resource acquisition.
- Kernel templates can reserve explicit dependency slots.
- Binding parity improves because the ordering rule is global.
- The distinction remains visible in docs, tests, and audits.

## Rejected alternatives

- A single dependency list with convention-based ordering.
- Letting handlers or transport adapters perform security checks ad hoc.
- Running ordinary deps before authn/authz-oriented deps for convenience.

