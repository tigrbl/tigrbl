<div align="center">
<h1>tigrbl</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, OpenAPI, OpenRPC, typed validation, hooks, diagnostics, and engine plugins.</strong></p>
<a href="https://pypi.org/project/tigrbl/"><img src="https://img.shields.io/pypi/v/tigrbl?label=PyPI" alt="PyPI version for tigrbl"/></a>
<a href="https://pypi.org/project/tigrbl/"><img src="https://static.pepy.tech/badge/tigrbl" alt="Downloads for tigrbl"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md.svg?label=hits" alt="Repository hits for tigrbl README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl"/></a>
</div>

## What is tigrbl?

Schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, OpenAPI, OpenRPC, typed validation, hooks, diagnostics, and engine plugins.

## Why use tigrbl?

Use it when you want the public Tigrbl authoring surface in one install target instead of composing split packages by hand.

## When should I install tigrbl?

Install it for application projects, examples, service skeletons, and teams that want REST, JSON-RPC, streaming, SSE, WebSocket, docs, schemas, engines, and CLI support from one facade.

## Who is tigrbl for?

Application developers, platform teams, and service owners building schema-first Python APIs.

## Where does tigrbl fit?

`tigrbl` lives at `pkgs/core/tigrbl` and serves schema-first service authoring, REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, docs, engines, and CLI workflows.

## How does tigrbl work?

It re-exports stable author-facing classes and decorators while delegating resident behavior to core, base, runtime, kernel, atoms, ORM, and operation packages.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl
```

```bash
pip install tigrbl
```

Optional extras declared in `pyproject.toml`:

```bash
pip install "tigrbl[postgres,servers,templates,tests]"
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl`](https://pypi.org/project/tigrbl/) |
| Repository path | [`pkgs/core/tigrbl`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl) |
| Python import root | `tigrbl` |
| Console scripts | `tigrbl` |
| Entry points | none declared |
| Optional extras | `postgres`, `servers`, `templates`, `tests` |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

## What It Owns

`tigrbl` owns the `public facade package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl`: __main__, canonical_json, cli, config/, ddl/, decorators/, engine/, factories/, hook/, middlewares/, op/, orm/

Facade orientation:
- Authoring API: app/router factories, table helpers, column helpers, schema helpers, operation decorators, hook decorators, response decorators, and engine decorators.
- Compatibility imports: facade modules such as `tigrbl.op`, `tigrbl.config`, `tigrbl.schema`, `tigrbl.ddl`, `tigrbl.security`, and `tigrbl.system` forward into the split packages that now own the implementation.
- Runtime projection: model operations are compiled into REST bindings, JSON-RPC methods, HTTP streams, SSE responses, WebSocket channels, WebTransport-aware runtime units, OpenAPI, OpenRPC, diagnostics, schemas, and engine-backed handlers.
- Operational boundary: this package is the application-facing install target; lower-level packages own specs, atoms, kernel planning, runtime execution, base abstractions, concrete adapters, ORM helpers, and engine plugins.

## Public API and Import Surface

- Import roots: `tigrbl`.
- Public symbols: `APIKey`, `Alias`, `App`, `AppBase`, `AppSpec`, `Arity`, `BINDING_PROFILE_EXCHANGE_SUPPORT`, `BackgroundTask`, `Binding`, `BindingRegistry`, `BindingRegistrySpec`, `BindingSpec`.
- Workspace dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/), [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/), [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/).
- External runtime dependencies: `pydantic>=2.0.0`, `sqlalchemy>=2.0`, `aiosqlite>=0.19.0`, `httpx>=0.27.0`, `greenlet>=3.2.3`, `uvicorn`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl"))
PY
```

### Create a small Tigrbl app shell

```python
from tigrbl import TigrblApp, TigrblRouter

app = TigrblApp()
router = TigrblRouter()
app.include_router(router)
```

### Use author-facing decorators

```python
from tigrbl import get, post

@get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@post("/items")
def create_item(payload: dict) -> dict:
    return payload
```

### Run the console entry point

```bash
tigrbl --help
python -m tigrbl --help
```

## Framework Catalog

Tigrbl is organized as a split framework behind this facade:

| Layer | Package | Responsibility |
|---|---|---|
| Facade | `tigrbl` | Public authoring imports, shortcuts, compatibility modules, CLI entry point, and application-facing docs. |
| Core specs | `tigrbl-core` | App, router, table, column, op, hook, schema, response, binding, engine, storage, path, docs, session, and middleware specs. |
| Base contracts | `tigrbl-base` | Abstract app/router/table/session/request/response/binding/security/middleware/storage interfaces and mapping helpers. |
| Concrete adapters | `tigrbl-concrete` | Concrete app/router/table/response/request/security/decorator/engine/system/transport implementations. |
| Atoms | `tigrbl-atoms` | Phase names, stage transitions, typed contexts, ingress/dispatch/wire/storage/handler/egress/error atoms, transaction atoms, batch atoms, and transport atoms. |
| Kernel | `tigrbl-kernel` | Operation-view compilation, hook ordering, labels, packed plans, protocol chains, lifecycle rows, event keys, capability masks, and dispatch plans. |
| Runtime | `tigrbl-runtime` | Runtime-owned routing, request execution, framing atoms, transport channels, and default kernel integration. |
| Operation packs | `tigrbl-ops-oltp`, `tigrbl-ops-olap`, `tigrbl-ops-realtime` | Canonical operation definitions for CRUD, analytics, and realtime/streaming workloads. |
| ORM | `tigrbl-orm` | SQLAlchemy-facing table and mixin helpers used by application models. |
| Engines | `tigrbl-engine-*` | Persistence, cache, queue, rate, bloom, dedupe, dataframe, warehouse, and database engine integrations. |

Use the facade for application code unless you are maintaining a framework layer, testing a boundary in isolation, or writing a package that intentionally plugs into one of the lower layers.

## Authoring BCP

The facade is the normal application authoring surface. Use `docs/developer/AUTHORING_BCP.md` for the full policy; this package README keeps the public-package guidance explicit because it is the README most application developers see first.

If you are translating concepts from Starlette, FastAPI, Flask, ASGI 3,
WebSocket, WebTransport, SQLAlchemy, or backend-specific SQL engines, start with
[`docs/developer/EQUIVALENCE_INDEX.md`](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/EQUIVALENCE_INDEX.md).
Those guides describe analogous lower-layer concepts while keeping Tigrbl-owned
authoring surfaces as the application contract.

Do:

- Do import application-facing classes, decorators, helpers, and shortcuts from `tigrbl` unless you are intentionally maintaining a lower-level package. Why: the facade is the supported application contract and hides lower-layer package splits.
- Do create services with `TigrblApp`, `TigrblRouter`, facade route/operation decorators, table helpers, column helpers, hook decorators, response decorators, schema helpers, and engine decorators. Why: these entry points are visible to runtime planning, docs, diagnostics, schemas, and tests.
- Do model domain actions as Tigrbl operations, including canonical CRUD operations, operation-pack verbs, or explicit custom operation specs. Why: operations are the unit Tigrbl can project consistently across protocol surfaces.
- Do use operation handlers through Tigrbl specs and kernel/runtime dispatch so REST, JSON-RPC, HTTP streams, SSE, WebSocket, WebTransport-aware runtime units, OpenAPI, OpenRPC, diagnostics, schemas, hooks, and tests stay aligned. Why: handler dispatch is where protocol projection and lifecycle guarantees meet.
- Do express field behavior through Tigrbl table, column, datatype, storage, IO, request, response, and operation specs. Why: specs are the shared source for storage lowering, wire schemas, docs, runtime planning, hooks, and diagnostics.
- Do use `get_schema(...)` or schema helpers for operation request/response payloads. Why: generated schemas keep payloads aligned with operation specs and docs.
- Do bind engines declaratively at app, router, table, or operation scope. Why: declarative binding lets the runtime own session selection, transaction scope, diagnostics, and backend-specific behavior.
- Do use lifecycle hooks for policy, validation, enrichment, audit, response shaping, and post-response work. Why: hooks make policy visible to lifecycle ordering, diagnostics, tests, and transport-independent execution.
- Do use `/system/methodz`, `/system/hookz`, `/system/kernelz`, OpenAPI, and OpenRPC to inspect the registered framework state. Why: these surfaces show the compiled Tigrbl state instead of a lower-level framework's partial view.

Do not:

- Do not author application endpoints with FastAPI `FastAPI`, `APIRouter`, dependency wiring, route decorators, middleware registration, docs generation, or lifecycle hooks. Why: that makes FastAPI the application contract instead of Tigrbl's operation, binding, hook, schema, docs, and diagnostics contract.
- Do not author application endpoints with Starlette route, request, response, middleware, background-task, or lifecycle classes. Why: Starlette is a lower-level runtime substrate here, not the application-facing authoring surface.
- Do not author application endpoints with Flask `Flask`, `Blueprint`, route decorators, request/response globals, `MethodView`, extension registration, or lifecycle hooks. Why: Flask route objects cannot preserve Tigrbl's shared operation inventory, schema generation, lifecycle phases, or transport plan.
- Do not use raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the primary application authoring surface when Tigrbl column helpers or specs can represent the field behavior. Why: raw ORM declarations are only one lowering target and cannot carry the full storage, IO, validation, docs, hook, and runtime contract.
- Do not build ad-hoc SQLAlchemy engines, sessions, or sessionmakers inside request handlers. Why: ad-hoc construction bypasses declarative engine binding, session policy, pooling, diagnostics, tests, and backend adapters.
- Do not call direct database/session methods such as `flush()` or `commit()` from application hooks or handlers unless you are implementing a framework-level atom with the correct lifecycle guard contract. Why: direct calls bypass lifecycle guards and can commit partial state before hooks, errors, rollback handlers, or response shaping have run.
- Do not wrap model behavior in one-off route handlers when an operation spec can represent the behavior. Why: route wrappers hide behavior from protocol projection, docs, hooks, diagnostics, and tests.
- Do not bypass kernel/runtime plans when wiring REST, JSON-RPC, HTTP stream, SSE, WebSocket, or WebTransport behavior. Why: bypasses skip legality checks, lifecycle phases, transaction ownership, protocol framing policy, and fail-closed unsupported-combination handling.

Avoid:

- Avoid treating ASGI, FastAPI, Flask, Starlette, SQLAlchemy ORM materialization, or direct DB methods as the user-facing application contract. Tigrbl owns the authoring contract; lower-level libraries are implementation substrates behind Tigrbl-owned adapters, engines, tests, or benchmarks. Why: lower-level substrates are legal implementation tools, but not the supported application API.
- Avoid duplicating field behavior in SQLAlchemy, Pydantic, docs, and route handlers. Put reusable behavior in Tigrbl specs so storage, schema, docs, runtime, hooks, and diagnostics read the same source. Why: duplicated rules create stale validation, stale docs, and protocol-specific behavior differences.
- Avoid hand-written Pydantic envelopes for payloads that belong to a Tigrbl operation. Why: generated schemas keep request/response payloads aligned with operation specs and docs.
- Avoid transport-specific wrappers for authentication, authorization, validation, or dispatch when security dependencies, hooks, operation specs, or lifecycle phases can express the rule once. Why: transport-layer policy can make REST, JSON-RPC, streams, SSE, WebSocket, and WebTransport disagree about the same domain operation.
- Avoid teaching lower-level internals in application README examples unless the example is clearly marked as a test, benchmark, migration, engine adapter, or framework-internal compatibility surface. Why: examples without a boundary marker become accidental guidance.

## Default CRUD and Operation Semantics

The canonical default operation set is `create`, `read`, `update`, `replace`, `delete`, `list`, and `clear`. Tables can opt out, opt into a subset, or add explicit operation specs. Additional operation packs provide bulk, analytical, and realtime verbs such as `bulk_create`, `bulk_update`, `bulk_replace`, `bulk_merge`, `bulk_delete`, `count`, `exists`, `aggregate`, `group_by`, `tail`, `subscribe`, `publish`, `upload`, `download`, `append_chunk`, `checkpoint`, and transport-oriented handlers.

| Operation | REST shape | JSON-RPC shape | Arity | Semantics |
|---|---|---|---|---|
| `create` | `POST /{resource}` | `Model.create` | collection | Validate input, apply defaults/policies, persist one record, return the output schema. |
| `read` | `GET /{resource}/{id}` | `Model.read` | member | Fetch one record by identity and serialize through the output schema. |
| `update` | `PATCH /{resource}/{id}` | `Model.update` | member | Apply partial update semantics; omitted fields remain unchanged. |
| `replace` | `PUT /{resource}/{id}` | `Model.replace` | member | Apply replacement semantics; the submitted representation is the desired record shape. |
| `delete` | `DELETE /{resource}/{id}` | `Model.delete` | member | Remove or policy-delete one record and return the configured result envelope. |
| `list` | `GET /{resource}` | `Model.list` | collection | Resolve filters, pagination, ordering, visibility policy, and output collection shape. |
| `clear` | `DELETE /{resource}` | `Model.clear` | collection | Delete a collection according to policy and filter configuration. |
| `bulk_create` | `POST /{resource}` | `Model.bulk_create` | collection | Create many records from an array of row objects and return the created row outputs. |
| `bulk_update` | `PATCH /{resource}` | `Model.bulk_update` | collection | Patch many existing records by primary key and return the updated row outputs. |
| `bulk_replace` | `PUT /{resource}` | `Model.bulk_replace` | collection | Replace many existing records by primary key and return the replaced row outputs. |
| `bulk_merge` | `PATCH /{resource}` | `Model.bulk_merge` | collection | Upsert or merge many records by primary key and return the resulting row outputs. |
| `bulk_delete` | `DELETE /{resource}` | `Model.bulk_delete` | collection | Delete many records by primary key and return a deleted-count envelope. |
| `custom` | op-defined | op-defined | op-defined | Use explicit `op_ctx`/operation specs for domain-specific verbs while keeping schemas, hooks, and policies unified. |

Route conflicts are intentional. A collection `POST` cannot simultaneously mean scalar `create` and `bulk_create` on the same REST path, and a collection `DELETE` cannot simultaneously mean `clear` and `bulk_delete`. JSON-RPC methods remain independently addressable by method name, so RPC is the right surface when both scalar and bulk forms must be exposed without path ambiguity.

## Bulk Operation Shape Reference

Bulk operations are collection-arity operations. REST binds them to the collection path, while JSON-RPC binds them to `Model.<bulk_op>`. The public wire shape is intentionally simple: row bulk operations take a JSON array of row objects, and `bulk_delete` takes a JSON array of primary-key values. Wrapper objects such as `{ "data": ... }`, `{ "payload": ... }`, `{ "body": ... }`, and `{ "item": ... }` are rejected unless those names are real schema fields for the operation.

| Operation | REST request | JSON-RPC params | Success response | Required shape rules |
|---|---|---|---|---|
| `bulk_create` | `POST /{resource}` with `[{...row}, {...row}]` | `[{...row}, {...row}]` | `[{...created_row}, {...created_row}]` | Each item is a create input row. Primary keys may be supplied or generated according to the table schema. Empty input creates nothing and returns `[]`. |
| `bulk_update` | `PATCH /{resource}` with `[{pk: value, ...patch}, ...]` | `[{pk: value, ...patch}, ...]` | `[{...updated_row}, ...]` | Each item must include the model primary-key field. Non-PK fields are patched; omitted mutable fields remain unchanged. Immutable columns for `update` are skipped. |
| `bulk_replace` | `PUT /{resource}` with `[{pk: value, ...replacement}, ...]` | `[{pk: value, ...replacement}, ...]` | `[{...replaced_row}, ...]` | Each item must include the model primary-key field. Replacement semantics apply per row: missing mutable attributes are cleared according to replace behavior, while immutable columns for `replace` are skipped. |
| `bulk_merge` | `PATCH /{resource}` with `[{pk: value, ...fields}, ...]` | `[{pk: value, ...fields}, ...]` | `[{...merged_or_created_row}, ...]` | Rows with an existing primary key are merged; rows with no key or a non-existing key are created/upserted. Existing-row merge follows the scalar `merge` semantics. |
| `bulk_delete` | `DELETE /{resource}` with `[pk1, pk2]` | `[pk1, pk2]` | `{ "deleted": N }` | Input is a sequence of primary-key values. The schema/docs layer may expose an `ids` wrapper for component naming, but REST and JSON-RPC call paths normalize a bare ID list. Empty input returns `{ "deleted": 0 }`. |

Example REST payloads:

```json
[
  { "id": "w-1", "name": "first" },
  { "id": "w-2", "name": "second" }
]
```

```json
["w-1", "w-2"]
```

Example JSON-RPC calls:

```json
{
  "jsonrpc": "2.0",
  "method": "Widget.bulk_update",
  "params": [
    { "id": "w-1", "name": "renamed" },
    { "id": "w-2", "name": "retitled" }
  ],
  "id": 1
}
```

```json
{
  "jsonrpc": "2.0",
  "method": "Widget.bulk_delete",
  "params": ["w-1", "w-2"],
  "id": 2
}
```

Bulk operations are not part of the minimal canonical default set. They are enabled by operation specs, mixins such as `BulkCapable`, `Replaceable`, and `Mergeable`, or explicit table configuration. `bulk_replace` depends on replacement support, and `bulk_merge` depends on merge support. When a bulk REST route claims the same collection method as a scalar route, the bulk route suppresses the conflicting scalar REST route; the scalar JSON-RPC method can still be exposed by name.

## REST, JSON-RPC, and Transport Projection

Tigrbl projects the same operation inventory across multiple protocol surfaces while keeping protocol, carrier, exchange, stream direction, and framing separate. The full public matrix is in [`docs/developer/TRANSPORTS_AND_FRAMING.md`](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/TRANSPORTS_AND_FRAMING.md).

| Surface | Binding family | Framing | Primary use |
|---|---|---|---|
| REST over HTTP/HTTPS | request | JSON | Resource-oriented CRUD and conventional HTTP clients. |
| JSON-RPC over HTTP/HTTPS | request | JSON-RPC | Method-oriented clients, batch-capable RPC contracts, and OpenRPC generation. |
| HTTP stream | stream | stream or configured stream framing | Server-streaming outputs and progressive responses. |
| SSE | stream | SSE | Browser-friendly event streams. |
| WebSocket/WSS | message | text or JSON-RPC when negotiated | Bidirectional message workflows. |
| WebTransport | session, stream, or datagram | no top-level app framing; lane-local framing only | Session, stream, and datagram transports with fail-closed lane validation. |
| h11 / h2 / h3 / QUIC carrier metadata | delegated server/runtime boundary | binding-dependent | Serving-stack protocol mechanics, runtime capability metadata, and deployment controls. |

The framework keeps protocol, exchange, and framing separate. For example, strict JSON-RPC document framing is `jsonrpc`; newline-delimited JSON-RPC should be modeled distinctly rather than collapsed into plain `ndjson`. Unsupported combinations fail closed during binding or runtime planning instead of being guessed. Tigrbl owns binding declarations, runtime planning, channel metadata, and frame codecs; the serving/runtime stack owns wire-level HTTP/1.1, HTTP/2, HTTP/3, QUIC, TLS termination, HPACK, QPACK, ALPN, and flow control.

## Request Lifecycle and Hook Phases

Runtime-owned routing flows through stable phases. Hooks attach to phases, atoms provide framework work, and the kernel records the plan used for each model operation.

| Phase | Role |
|---|---|
| `INGRESS_BEGIN` | Start request or transport-unit handling and initialize context. |
| `INGRESS_PARSE` | Parse transport payloads, request metadata, path variables, query data, or message bodies. |
| `INGRESS_DISPATCH` | Resolve the target operation, binding, and protocol subevent. |
| `PRE_TX_BEGIN` | Run pre-transaction checks before a database transaction exists. |
| `START_TX` | Open or attach transaction/session state when the operation requires it. |
| `PRE_HANDLER` | Resolve dependencies, validate inputs, enforce policy, and prepare handler state. |
| `HANDLER` | Execute the operation handler or system handler. |
| `POST_HANDLER` | Normalize handler output and run in-transaction post-processing. |
| `PRE_COMMIT` | Run final in-transaction checks before commit. |
| `TX_COMMIT` | Flush/commit when Tigrbl owns the transaction; also exposed historically as `END_TX`. |
| `POST_COMMIT` | Run committed-side effects before response shaping. |
| `EGRESS_SHAPE` | Build response envelopes, apply masks, negotiate output shape, and prepare transport response data. |
| `EGRESS_FINALIZE` | Apply headers/status/renderers and finalize transport response. |
| `POST_RESPONSE` | Run after-response work that should not affect the returned payload. |
| `ON_*_ERROR` | Phase-specific error handling; falls back to `ON_ERROR` when no specific chain handles the failure. |
| `TX_ROLLBACK` | Roll back transaction-owned work and perform cleanup; also exposed historically as `ON_ROLLBACK`. |

Happy path:

```text
INGRESS_BEGIN
INGRESS_PARSE
INGRESS_DISPATCH
PRE_TX_BEGIN
START_TX
PRE_HANDLER
HANDLER
POST_HANDLER
PRE_COMMIT
TX_COMMIT
POST_COMMIT
EGRESS_SHAPE
EGRESS_FINALIZE
POST_RESPONSE
```

Use hooks for policy, validation, enrichment, audit, response shaping, and post-response work. Keep core persistence and transport handling inside ops and atoms so REST, JSON-RPC, diagnostics, and schemas stay aligned.

```python
from tigrbl import hook_ctx

@hook_ctx(ops="create", phase="PRE_HANDLER")
async def validate_name(ctx):
    payload = ctx["request"].payload
    if payload.get("name") == "reserved":
        raise ValueError("reserved name")
```

Hooks can also be registered imperatively on the model or composed by packages that build operation specs. Running apps can expose `/system/hookz` to inspect registered hook order and `/system/kernelz` to inspect the compiled phase plan.

## Step Types and Kernel Labels

Execution plans are composed from labeled steps:

| Step type | Owner | Purpose |
|---|---|---|
| `secdep` | Application or security package | Authentication and authorization dependencies that run before ordinary dependencies. |
| `dep` | Application or extension package | General dependency resolution and request context hydration. |
| `hook:sys` | Tigrbl | Built-in system hooks for runtime behavior, transaction handling, schema work, and transport work. |
| `hook:wire` | Application or extension package | User hooks registered through decorators or specs. |
| `atom:<domain>:<subject>` | Tigrbl atoms/kernel | Small runtime units such as ingress parsing, dispatch, validation, handler invocation, response shaping, or transport emission. |

Kernel labels make execution order reviewable, for example `PRE_HANDLER:hook:wire:myapp.audit@PRE_HANDLER` or `EGRESS_SHAPE:atom:wire:dump`. Treat labels as diagnostics, not as a stable replacement for the public decorator/spec APIs.

## Engine and Session Semantics

Engines are declared through specs, providers, decorators, or concrete engine instances. Resolution chooses the most specific binding:

```text
operation > table/model > router > app > defaults
```

Use engine specs and Tigrbl's engine decorators instead of creating ad-hoc SQLAlchemy engines inside handlers. This keeps transaction ownership, routing, diagnostics, engine plugins, and tests coherent.

```python
from tigrbl.decorators.engine import engine_ctx
from tigrbl.engine.shortcuts import engine_spec

db = engine_spec(kind="sqlite", mode="memory")

@engine_ctx(db)
class Item:
    __tablename__ = "items"
```

Database sessions are guarded by lifecycle phase. Do not call `flush()` or `commit()` directly from application hooks or handlers unless you are implementing a framework-level atom with the correct guard contract. Let `START_TX`, `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, and `TX_COMMIT` own transaction progression.

## Configuration and Schema Precedence

Tigrbl resolves configuration by layering broad defaults first and specific intent last:

```text
per-request overrides > operation spec > column spec > table spec > router spec > app spec > framework defaults
```

Use that same mental model for schema, response, path, engine, and operation behavior. Put shared policy at app/router scope, model-specific behavior at table scope, field behavior at column scope, and exceptional behavior in operation specs or request overrides.

Common table-level declarations include:

- `__tigrbl_request_extras__` and `__tigrbl_response_extras__` for operation-scoped virtual fields.
- `__tigrbl_register_hooks__` or hook decorators for lifecycle customization.
- `__tigrbl_nested_paths__` for hierarchical REST paths.
- `__tigrbl_allow_anon__` for anonymous operation access.
- `__tigrbl_owner_policy__` and `__tigrbl_tenant_policy__` for ownership and tenancy injection.
- `__tigrbl_verb_aliases__` and `__tigrbl_verb_alias_policy__` for operation naming and alias behavior.

## Best Practices

- Use `tigrbl` facade imports in application code; import split packages directly only for framework extension work.
- Model domain actions as operations, not ad-hoc routes, so REST, JSON-RPC, schemas, hooks, OpenAPI, OpenRPC, and diagnostics stay in sync.
- Use `get_schema(...)` or schema helpers for request/response envelopes instead of hand-rolled Pydantic classes when the payload belongs to a Tigrbl operation.
- Keep `Table` first in model inheritance when using ORM table classes so table inspection and MRO-sensitive behavior stay deterministic.
- Bind engines declaratively at app, router, table, or operation scope; do not create engines inside request handlers.
- Let the lifecycle own transaction boundaries; avoid direct `flush()`, `commit()`, and SQLAlchemy session mutation from user hooks.
- Put authentication/authorization in security dependencies or `PRE_HANDLER` hooks, not in transport-specific route wrappers.
- Use `/system/hookz`, `/system/kernelz`, docs endpoints, OpenAPI, and OpenRPC outputs as operational inspection surfaces during debugging.
- Treat unsupported transport/framing combinations as unsupported, not broken. Preserve fail-closed behavior unless the underlying binding and runtime packages are intentionally extended.

## How To Choose This Package

Choose `tigrbl` when you want the full public facade: app composition, schema-first routing, REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, docs generation, engine integration, and CLI workflow. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) only when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Equivalence guide index](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/EQUIVALENCE_INDEX.md)
- [Application authoring equivalence](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/AUTHORING_EQUIVALENCE.md)
- [Router and table equivalence](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/ROUTER_TABLE_EQUIVALENCE.md)
- [Transport equivalence](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/TRANSPORT_EQUIVALENCE.md)
- [Engine and SQL equivalence](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/ENGINE_SQL_EQUIVALENCE.md)
- [Transports and framing](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/TRANSPORTS_AND_FRAMING.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [Next steps](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/NEXT_STEPS.md)
- [Documentation pointers](https://github.com/tigrbl/tigrbl/blob/master/docs/governance/DOC_POINTERS.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/core/tigrbl](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
