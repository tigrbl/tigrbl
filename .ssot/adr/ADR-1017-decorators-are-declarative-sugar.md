# ADR-0017 â€” Decorators Are Declarative Sugar

- **Status:** Proposed
- **Date:** 2026-04-14
- **Related ADRs:** ADR-0003, ADR-0004, ADR-0018, ADR-0019

## Context

The public authoring surface will continue to use decorators, but decorators are easy places to smuggle in hidden runtime behavior.
Tigrbl needs a design-pattern ADR that keeps decorators aligned with the spec-first model rather than letting them become another semantic layer.

## Decision

1. Decorators are authoring conveniences over canonical declarative objects.
2. A decorator may normalize inputs and assemble canonical specs, but it may not introduce hidden semantics unavailable in the canonical declarative layer.
3. Decorators do not own runtime behavior; they declare it.
4. Decorator expansion must be deterministic and inspectable.
5. Decorator APIs should prefer explicitness over magic when the choice changes canonical semantics.
6. If a decorator cannot be explained as declarative sugar over canonical forms, it is not the right abstraction.

## Consequences

- Public APIs stay ergonomic without creating a second semantic system.
- Tests can validate decorator expansion against canonical spec objects.
- Alias and pattern ADRs can build on a constrained decorator philosophy.
- Refactoring the runtime does not require rewriting the public API contract.

## Rejected alternatives

- Decorators that allocate live runtime objects as part of declaration.
- Transport-specific decorator semantics that bypass canonical specs.
- Divergent decorator-only features.

