# Canonical HTTP Route Registration

Date: 2026-04-16
Kind: repo-local

## Intent

This document defines the canonical HTTP route registration model for the active line.

## Canonical model

- A registered HTTP route is a concrete custom op alias with one or more `HttpRestBindingSpec` bindings.
- `route_ctx(...)` is the decorator-first alias that expands into that shape during materialization.
- `register_http_route(...)` is the imperative helper that registers the same shape directly onto concrete app/router owners.

## Required registration fields

`register_http_route(...)` requires:

- `path`
- `methods`
- `alias`
- `endpoint`

The helper normalizes the HTTP path, normalizes the verb set, and stores the resulting op on the synthetic concrete route model.

## Synthetic route model

- Concrete route-backed ops are stored on `__tigrbl_system_routes__`.
- The synthetic route model is not limited to docs endpoints; it is the shared owner for concrete route-backed custom ops.
- Re-registering the same alias updates the existing op entry instead of creating duplicate op rows.

## System documents

- HTTP system-document mounts such as `/openapi.json`, `/docs`, `/openrpc.json`, `/lens`, `/schemas.json`, `/asyncapi.json`, favicon endpoints, and diagnostics endpoints register through `register_http_route(...)`.
- The `system` package may call the helper, but it does not define canonical route registration behavior.

## Traceability

- ADR: `adr/ADR-0027-route-aliases-expand-to-concrete-http-op-specs.md`
- Tests:
  - `pkgs/core/tigrbl_tests/tests/unit/test_http_route_registration.py`
  - `pkgs/core/tigrbl_tests/tests/unit/decorators/test_phase1_declarative_surface.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_system_docs_builders.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py`
