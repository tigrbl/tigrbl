# Target Boundary

## Frozen current target boundary

Stable release `0.3.18` remains the frozen current-target boundary.

Tigrbl owns:

- application semantics
- API semantics
- authentication / authorization semantics
- OpenAPI / OpenRPC docs emission within the framework boundary
- framework-owned operator surfaces
- compatibility with Tigrcorn, Uvicorn, Hypercorn, and Gunicorn

## Security model

Security is OAS 3.1 security-scheme first.

## Retained exact RFC rows for the frozen current cycle

After the Phase 6 boundary review, the frozen cycle retains these exact RFC rows at the framework boundary:

- RFC 7235 — framework-owned HTTP authentication challenge semantics
- RFC 7617 — HTTP Basic parsing and challenge behavior
- RFC 6750 — HTTP Bearer token parsing and challenge behavior

These rows are retained because the framework owns concrete runtime behavior and negative-test evidence for them in the frozen release history.

## Exact RFC / OIDC rows explicitly de-scoped from the frozen current cycle

The following exact rows are no longer part of the frozen-cycle certification boundary:

- OIDC Core 1.0 exact closure
- RFC 6749 exact OAuth 2.0 closure
- RFC 7519 exact JWT closure
- RFC 7636 exact PKCE closure
- RFC 8414 exact authorization-server metadata closure
- RFC 8705 exact OAuth 2.0 mutual-TLS closure
- RFC 9110 exact framework-owned semantics row
- RFC 9449 exact DPoP closure
- OIDC discovery/docs route surface

The OAS security-scheme rows for `oauth2`, `openIdConnect`, and `mutualTLS` remain in-boundary for the frozen release. What is de-scoped here is the broader exact RFC-closure claim for those families.

## Explicitly deferred from frozen current-target certification

The following are active next-target items and do not alter the frozen `0.3.18` certification boundary:

- canonical datatype system as active semantic center
- `DataTypeSpec`, `StorageTypeRef`, `TypeAdapter`, `TypeRegistry`, and builtin datatype adapters
- `ColumnSpec.datatype` and related spec integration
- engine lowering and bridge contracts including `EngineTypeLowerer`, `EngineRegistry`, and `EngineDatatypeBridge`
- table spec / portability / interoperability
- reflection-driven round-trip schema recovery
- full multi-engine table semantics beyond column types

## Explicitly out of current framework boundary

The following remain server/runtime concerns for the frozen cycle:

- HTTP/1.1 / HTTP/2 / HTTP/3 framework-owned conformance
- QUIC
- HPACK
- QPACK
- server-side TLS termination

## Docs/UI rows explicitly de-scoped in Phase 7

- AsyncAPI UI (while `/asyncapi.json` stays in scope)
- JSON Schema UI (while `/schemas.json` stays in scope)
- OIDC discovery/docs surface

## Generic auth-surface decision

The framework keeps auth dependency/hook-based only in the frozen cycle and does not add a new monolithic generic auth middleware abstraction.

## Post-promotion handoff rule

The active `0.3.19.dev1` line must keep next-target datatype/table work isolated from the frozen `0.3.18` release history until a later governed cycle declares and proves a new boundary.
