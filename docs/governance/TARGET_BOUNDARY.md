# Target Boundary

## Current target boundary

Tigrbl currently owns:

- application semantics
- API semantics
- authentication / authorization semantics
- OpenAPI / OpenRPC docs emission within the framework boundary
- framework-owned operator surfaces
- compatibility with Tigrcorn, Uvicorn, Hypercorn, and Gunicorn

## Security model

Security is OAS 3.1 security-scheme first.

## Explicitly deferred from current-target certification

The following are next-target items and do not block current-target closure:

- canonical datatype system as active semantic center
- table spec / portability / interoperability
- reflection-driven round-trip schema recovery
- full multi-engine table semantics beyond column types

## Explicitly out of current framework boundary

The following remain server/runtime concerns for this cycle:

- HTTP/1.1 / HTTP/2 / HTTP/3 framework-owned conformance
- QUIC
- HPACK
- QPACK
- server-side TLS termination
