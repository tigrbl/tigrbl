# ADR-1028: ADR-0027 - Route Aliases Expand to Concrete HTTP Op Specs

# ADR-0027 - Route Aliases Expand to Concrete HTTP Op Specs

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0003, ADR-0006, ADR-0017, ADR-0018

## Context

Tigrbl previously described some HTTP route registration paths as "runtime routes" and placed canonical registration helpers under `tigrbl_concrete.system.docs`. That made ordinary HTTP route registration look like a separate abstraction rather than what it really is: concrete `op_ctx`-style custom operations carrying `HttpRestBindingSpec` bindings.

The route model also mixed deprecated `tigrbl_canon` compatibility code into a surface that is no longer supported.

## Decision

1. An HTTP route is a concrete custom op alias plus at least one `HttpRestBindingSpec`.
2. `route_ctx(...)` remains the decorator-first alias for declaring that shape.
3. `register_http_route(...)` is the imperative helper for materializing the same shape onto app/router owners.
4. Canonical HTTP route registration lives in `tigrbl_concrete`, not in `tigrbl_concrete.system`.
5. System document endpoints use the same `register_http_route(...)` helper as other HTTP routes.
6. Deprecated `tigrbl_canon` route-registration shims are removed rather than preserved.
7. "Runtime route" is not canonical terminology for HTTP route registration.

## Consequences

- HTTP route registration is inspectable as ordinary op/binding materialization.
- System document routes and custom user routes share one concrete registration path.
- Kernel-plan-visible route bindings come from one source of truth.
- Deprecated compatibility layers stop defining the API surface.

## Rejected alternatives

- Keeping a docs-owned HTTP route registration helper.
- Preserving `tigrbl_canon` compatibility shims for route registration.
- Treating HTTP routes as a separate abstraction from op alias expansion.

