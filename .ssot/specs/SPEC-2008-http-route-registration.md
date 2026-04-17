# Canonical HTTP Route Registration

﻿
Date: 2026-04-16
Kind: repo-local

## Intent

This document defines the canonical HTTP route model for the active line.

## Canonical model

- Module-level `route_ctx(...)` and module-level `route(...)` are not part of the active declarative surface.
- Module-level `get/post/put/patch/delete` are REST-specific decorator aliases over `op_ctx(...)`.
- Those decorators construct `HttpRestBindingSpec` values and pass them through `op_ctx(bindings=...)`.
- Imperative `Router.route/get/post/...` and `App.route/get/post/...` create `Route` records and normalize route-backed ops into the owner-local `__tigrbl_route_ops__` carrier.
- There is no separate HTTP route registration subsystem and no `register_http_route(...)` helper.

## Binding and metadata ownership

- Transport facts live in `HttpRestBindingSpec`.
- Op semantics live in `OpSpec`.
- Route-facing documentation/runtime policy lives on `Route`.
- `inherit_owner_dependencies` is the generic route policy flag used by documentation/system routes that should not inherit owner dependencies.

## Normalization rules

- Direct imperative routes and mounted imperative routes normalize into `__tigrbl_route_ops__`.
- The normalized carrier is an owner-local spec graph node, not a separate public subsystem.
- Reusing the same alias merges HTTP bindings by alias and path rather than creating duplicate op rows.
- Mount prefixes must be preserved on both the mounted `Route` and the normalized binding specs.

## Documentation endpoints

- `/openapi.*`, `/docs`, `/openrpc.json`, `/lens`, `/schemas.json`, and `/asyncapi.json` mount as ordinary routes.
- Those routes also normalize into `__tigrbl_route_ops__`.
- OpenAPI reads route-facing metadata from `Route`; OpenRPC, AsyncAPI, and JSON Schema continue to read their canonical op/binding/schema sources.

## Traceability

- ADRs:
  - `.ssot/adr/ADR-1028-route-aliases-expand-to-concrete-http-op-specs.md`
  - `.ssot/adr/ADR-1030-documentation-support-uses-canonical-metadata-sources.md`
- Tests:
  - `pkgs/core/tigrbl_tests/tests/unit/test_http_route_registration.py`
  - `pkgs/core/tigrbl_tests/tests/unit/decorators/test_phase1_declarative_surface.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_system_docs_builders.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py`
