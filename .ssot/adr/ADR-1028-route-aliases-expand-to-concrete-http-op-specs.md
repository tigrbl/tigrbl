# ADR-0027 - Binding-First REST Decorators and Route-Backed Spec Normalization

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0003, ADR-0006, ADR-0017, ADR-0018, ADR-0019

## Context

The active line no longer treats HTTP routes as a separate runtime abstraction. The old `route_ctx(...)` and `register_http_route(...)` model split declarative route aliases from imperative route mutation and introduced a second HTTP registration subsystem that did not align with the existing spec graph that the kernel already compiles.

At the same time, route-facing documentation metadata must still have an authoritative home, and documentation mounts must behave like ordinary routes rather than a docs-owned special case.

## Decision

1. Module-level `route_ctx(...)` and module-level `route(...)` are removed from the declarative surface.
2. Module-level `get(...)`, `post(...)`, `put(...)`, `patch(...)`, and `delete(...)` are REST-specific decorator aliases over `op_ctx(...)`.
3. Those REST decorators preset `HttpRestBindingSpec` values through `op_ctx(bindings=...)`; route-specific public fields are not added to `op_ctx(...)`.
4. `Router.route/get/post/...` and `App.route/get/post/...` remain imperative namespace APIs that create `Route` records.
5. Imperative routes normalize into the existing owner-local spec graph through the neutral `__tigrbl_route_ops__` carrier; there is no separate HTTP route registration subsystem and no public `register_http_route(...)` API.
6. `Route` remains the canonical home for route-facing documentation/runtime policy metadata, including `inherit_owner_dependencies`.
7. Kernel compilation is unchanged; kernel visibility comes from the existing nested spec graph after route-backed ops are normalized there.

## Consequences

- Declarative REST aliases and imperative route mutation converge on the same binding-first op shape.
- Direct routes, mounted routes, and documentation/system endpoints all become ordinary route-backed ops in the owner spec graph.
- Documentation support no longer depends on docs-policy imports inside route mutation code.
- The active line stops exposing a separate HTTP route registration helper.

## Rejected alternatives

- Keeping `route_ctx(...)` as a separate declarative abstraction.
- Keeping `register_http_route(...)` as a public or internal HTTP registration subsystem.
- Moving route-facing metadata into `HttpRestBindingSpec`.
