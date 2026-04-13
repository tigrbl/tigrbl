# Current Target

## Purpose

The current target defines what the repository is attempting to close for the present certification cycle.

## Gate A freeze status

- Freeze status: current target frozen for the current cycle
- Boundary freeze marker: `docs/conformance/gates/TARGET_FREEZE_CURRENT_CYCLE.json`
- Boundary freeze manifest: `docs/conformance/gates/GATE_A_BOUNDARY_FREEZE_MANIFEST.json`
- Update rule: any change to the current-target or boundary docs must include a synchronized `docs/conformance/CLAIM_REGISTRY.md` update and a regenerated boundary-freeze manifest/marker pair.

## In-boundary ownership

Tigrbl currently targets framework ownership over:

- application semantics
- API semantics
- auth semantics
- OAS 3.1 security-scheme-first docs and runtime alignment
- OpenAPI / OpenRPC docs emission within the framework boundary
- JSON-RPC / OpenRPC behavior within the framework boundary
- retained RFC auth rows at the framework boundary
- public operator surfaces owned by the framework
- support for Tigrcorn, Uvicorn, Hypercorn, and Gunicorn as supported serving paths

## Current-target surfaces already closed in checkpoints 5, 6, and 7

### OAS / docs / schema

- OpenAPI document emission at explicit `3.1.0`
- explicit `jsonSchemaDialect` set to Draft 2020-12
- `components.schemas`
- request body emission
- response emission
- path/query parameter emission
- `components.securitySchemes`
- operation-level `security` derived from `secdeps`
- mounted `/openapi.json`
- mounted Swagger UI at `/docs`
- mounted `/openrpc.json`
- mounted Lens / OpenRPC UI at `/lens`
- mounted JSON Schema bundle at `/schemas.json`
- mounted AsyncAPI spec at `/asyncapi.json`

### OAS security schemes

- `apiKey`
- `http` Basic
- `http` Bearer
- `oauth2`
- `openIdConnect`
- `mutualTLS`

### JSON-RPC / OpenRPC

- explicit JSON-RPC 2.0 target in the framework docs/runtime surface
- OpenRPC emission at explicit `1.2.6`
- JSON-RPC method envelope / batch / notification / docs alignment covered by current tests

### Retained exact RFC rows

- RFC 7235 — framework-owned HTTP authentication challenge semantics
- RFC 7617 — HTTP Basic parsing and challenge behavior
- RFC 6750 — HTTP Bearer token parsing and challenge behavior

### Operator surfaces closed in Phase 7

- static files
- cookies
- streaming responses
- WebSockets
- WHATWG SSE
- forms / multipart
- upload handling
- bounded built-in middleware catalog
- generic auth surface explicitly kept dependency/hook-based only

## Current-target rows explicitly de-scoped before Gate C

### Exact RFC rows de-scoped in Phase 6

- OIDC Core 1.0 exact closure
- RFC 6749 exact OAuth 2.0 closure
- RFC 7519 exact JWT closure
- RFC 7636 exact PKCE closure
- RFC 8414 exact authorization-server metadata closure
- RFC 8705 exact OAuth 2.0 mutual-TLS closure
- RFC 9110 exact framework-owned semantics row
- RFC 9449 exact DPoP closure

### Docs/UI rows de-scoped in Phase 7

- AsyncAPI UI (spec emission kept)
- JSON Schema UI (spec emission kept)
- OIDC discovery/docs surface

The de-scopes above keep the current target honest. They do **not** remove the already-closed OAS security-scheme rows for `oauth2`, `openIdConnect`, or `mutualTLS`, and they do **not** remove the emitted `/asyncapi.json` or `/schemas.json` surfaces.

## Current-target surfaces still missing

- unified `tigrbl` CLI and its target commands/flags

## Deferred next-target program

The datatype/table program remains deferred from current-target certification.
