# Equivalence Documentation Index

This index collects non-authoritative developer guides for comparing Tigrbl
authoring, transport, and engine surfaces to adjacent Python and SQL
frameworks. The governed source of truth remains `.ssot/`, authored ADRs,
authored specs, and release evidence.

Use these documents to translate concepts. Do not use them to replace the
authoring BCP or to assert support for undeclared transport, framing, engine,
or SQL behavior.

## Equivalence Rules

Equivalence in this repository means semantic parity for declared compatible
surfaces.

It does not require every operation to bind to every transport, and it does
not require transport envelopes, connection metadata, framing artifacts,
database dialects, or delivery mechanics to match unless those details are
declared as semantic behavior.

Unsupported, undeclared, or non-equivalent surfaces are excluded from
equivalence. They should fail closed or be described as out of boundary instead
of being coerced into a lossy comparison.

## Status Vocabulary

| Status | Meaning |
|---|---|
| Equivalent | The user-visible semantic outcome can be compared for a declared compatible surface. |
| Analogous | The surface serves a similar authoring purpose, but Tigrbl owns a different contract. |
| Projection-only | The lower layer is an input or output projection, not the semantic authority. |
| Delegated | Tigrbl models or consumes metadata, while another stack owns concrete mechanics. |
| Provisional | The surface is modeled or partially implemented and should not be presented as mature release-grade support. |
| Active line | The surface is implemented or tracked, but is not the main current-target support row. |
| Tigrbl-specific | The concept is owned by Tigrbl and has no direct Starlette, FastAPI, Flask, ASGI, SQLAlchemy, or SQL dialect equivalent. |
| Lower-layer only | The concept may appear in internals, adapters, tests, migrations, or benchmarks, but not as primary application authoring guidance. |
| Not equivalent | The surface differs in semantic ownership, lifecycle, or runtime guarantees. |
| Unsupported | The surface is intentionally rejected or out of the current support boundary. |

## Documents

| Need | Document | Scope |
|---|---|---|
| Application authoring comparison | `AUTHORING_EQUIVALENCE.md` | Tigrbl, Starlette, and FastAPI authoring concepts. |
| Router and table comparison | `ROUTER_TABLE_EQUIVALENCE.md` | Tigrbl, FastAPI, and Flask router/table concept maps. |
| Transport, ASGI 3, WebSocket, and WebTransport comparison | `TRANSPORT_EQUIVALENCE.md` | ASGI callable boundary, HTTP, streaming, SSE, WebSocket, WebTransport, and delegated carrier mechanics. |
| Engine and SQL comparison | `ENGINE_SQL_EQUIVALENCE.md` | Engine specs, SQLAlchemy substrate, engine plugins, datatype lowering, and SQL dialect differences. |
| Authoring policy | `AUTHORING_BCP.md` | Current application-facing Tigrbl authoring policy. |
| Transport and framing map | `TRANSPORTS_AND_FRAMING.md` | Current transport surface, framing matrix, fail-closed rules, and source pointers. |

## Generated Sections

The equivalence guides contain generated blocks for live facade exports,
binding/framing support, WebTransport lanes, engine package entry points,
datatype lowering, reflection hints, and built-in table profiles.

Use `python tools/docs/update_equivalence_docs.py --write` after changing the
source inputs. CI runs `tools/ci/validate_equivalence_docs.py` to fail when
those generated blocks drift.

## Reader Path

1. Start with `AUTHORING_BCP.md` to understand the current application
   authoring rule.
2. Use `AUTHORING_EQUIVALENCE.md` to translate Starlette or FastAPI concepts
   into Tigrbl-owned authoring surfaces.
3. Use `ROUTER_TABLE_EQUIVALENCE.md` when the question involves FastAPI
   routers, Flask blueprints, Tigrbl routers, or Tigrbl table/resource
   surfaces.
4. Use `TRANSPORT_EQUIVALENCE.md` when the question involves ASGI 3, HTTP,
   streaming, SSE, WebSocket, WebTransport, or delegated h11/h2/h3/QUIC
   behavior.
5. Use `ENGINE_SQL_EQUIVALENCE.md` when the question involves SQLAlchemy,
   database engines, SQL dialects, datatype lowering, sessions, transactions,
   or backend plugins.

## Boundary Notes

- Tigrbl application examples should use Tigrbl-owned authoring surfaces.
- Starlette, FastAPI, and Flask may appear in compatibility tests, benchmarks,
  migration notes, or framework-internal adapter discussion, but they are not
  the recommended Tigrbl application authoring contract.
- ASGI 3 is the runtime callable boundary. It is not the semantic authority for
  operation identity, delivery guarantees, framing, or transaction lifecycle.
- SQLAlchemy and database drivers are implementation substrates behind engine,
  storage, datatype, reflection, and transaction boundaries. They are not the
  primary Tigrbl application authoring surface.
