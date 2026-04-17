# Documentation Support and Metadata Ownership

Date: 2026-04-16
Kind: repo-local

## Supported outputs

The active line supports:

- OpenAPI
- OpenRPC
- AsyncAPI
- JSON Schema

## Canonical metadata sources

- OpenAPI consumes route-facing metadata from `Route` plus bound models and schemas.
- OpenRPC consumes canonical op specs, JSON-RPC bindings, and schemas.
- AsyncAPI consumes canonical transport bindings plus op/channel metadata.
- JSON Schema consumes canonical schema component metadata.

## Route behavior

- Documentation endpoints are ordinary imperative routes and ordinary normalized route-backed ops.
- Documentation/system mounts set `inherit_owner_dependencies=False` when owner dependency inheritance must be suppressed.
- No `surface_kind` abstraction is introduced.

## Traceability

- ADR: `adr/ADR-0029-documentation-support-uses-canonical-metadata-sources.md`
- Tests:
  - `pkgs/core/tigrbl_tests/tests/unit/test_http_route_registration.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_jsonrpc_openrpc.py`
  - `pkgs/core/tigrbl_tests/tests/unit/test_phase7_operator_surface_closure.py`
