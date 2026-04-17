# ADR-0029 - Documentation Support Uses Canonical Metadata Sources

- **Status:** Proposed
- **Date:** 2026-04-16
- **Related ADRs:** ADR-0006, ADR-0007, ADR-0027

## Context

Tigrbl supports multiple documentation outputs. Those outputs need stable metadata ownership rules so documentation mounting does not create its own route-registration subsystem and does not require a synthetic `surface_kind` abstraction.

## Decision

1. The active line supports OpenAPI, OpenRPC, AsyncAPI, and JSON Schema outputs.
2. OpenAPI consumes route-facing metadata from `Route`, together with bound models and schemas.
3. OpenRPC consumes canonical op, JSON-RPC binding, and schema metadata.
4. AsyncAPI consumes canonical transport binding and op/channel metadata.
5. JSON Schema consumes canonical schema component metadata.
6. Documentation endpoints such as `/openapi.json`, `/docs`, `/openrpc.json`, `/lens`, `/schemas.json`, and `/asyncapi.json` are ordinary imperative routes and ordinary normalized route-backed ops.
7. `inherit_owner_dependencies=False` is the generic route policy used for documentation/system endpoints where owner dependency inheritance must be suppressed.
8. No `surface_kind` field is introduced.

## Consequences

- Documentation builders consume canonical metadata instead of a docs-owned route registry.
- Documentation endpoints participate in the same route/op normalization path as other imperative routes.
- Documentation ownership remains explicit without adding a new surface taxonomy.

## Rejected alternatives

- Introducing a `surface_kind` abstraction.
- Treating documentation endpoints as a special registration subsystem.
- Moving OpenAPI route-facing metadata off `Route`.
