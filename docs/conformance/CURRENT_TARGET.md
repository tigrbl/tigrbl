# Current Target

## Purpose

The current target defines what the repository is attempting to close for the present certification cycle.

## In-boundary ownership

Tigrbl currently targets framework ownership over:

- application semantics
- API semantics
- auth semantics
- OAS 3.1 security-scheme-first docs and runtime alignment
- OpenAPI / OpenRPC docs emission within the framework boundary
- public operator surfaces owned by the framework
- support for Tigrcorn, Uvicorn, Hypercorn, and Gunicorn as supported serving paths

## Current-target surfaces already present

- OpenAPI 3.1 document emission
- Swagger UI
- OpenRPC JSON
- Lens / OpenRPC UI
- OAS security scheme modeling for `apiKey`, `http`, `oauth2`, `openIdConnect`, and `mutualTLS`
- generic auth plumbing through `AuthNProvider`, route/app auth configuration, security dependencies, and `OpSpec.secdeps`
- REST and JSON-RPC framework surfaces

## Current-target surfaces still partial

- explicit JSON Schema Draft 2020-12 closure
- explicit JSON-RPC 2.0 closure
- OIDC Core 1.0 closure
- RFC 7235 / 7617 / 6749 / 6750 / 7519 / 7636 / 8414 / 8705 / 9110 framework-owned semantics
- WebSockets
- static files
- cookies
- streaming responses
- built-in middleware catalog

## Current-target surfaces still missing

- RFC 9449 DPoP
- AsyncAPI docs UI
- JSON Schema docs UI
- OIDC discovery/docs surface
- WHATWG SSE
- forms / multipart
- upload handling
- unified `tigrbl` CLI and its target commands/flags

## Deferred next-target program

The datatype/table program is deferred from current-target certification.
