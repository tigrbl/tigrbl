![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/dm/tigrbl" alt="PyPI downloads for tigrbl"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl.svg" alt="Repository views for tigrbl"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/pyversions/tigrbl" alt="Supported Python versions for tigrbl"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/l/tigrbl" alt="PyPI license metadata for tigrbl"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/v/tigrbl?label=tigrbl&color=green" alt="PyPI version for tigrbl"/></a>
</p>

---

# Tigrbl

**Start building a Tigrbl API: [install `tigrbl` from PyPI](https://pypi.org/project/tigrbl/) and open the [facade package source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl).**

Tigrbl is the public facade package for building schema-first REST and JSON-RPC APIs from SQLAlchemy models with typed specs, canonical operation resolution, phase-aware hooks, dependency injection, security dependencies, runtime engines, and governed release evidence.

`tigrbl` is part of the Tigrbl package graph. It documents package-resident classes, concepts, extension points, and execution responsibilities while cross-linking to the facade, core specs, canonical mapping, runtime phases, concrete objects, operation packages, engine plugins, and Rust crates that complete the system.

## Public operation model

- `tigrbl` is the productized facade. It re-exports the author-facing objects that developers use first: `TigrblApp`, `TigrblRouter`, `TableBase`, `Base`, `Column`, `op_ctx`, `hook_ctx`, `schema_ctx`, `engine_ctx`, `allow_anon`, `created_at`, `updated_at`, REST helpers, JSON-RPC helpers, security helpers, and system docs builders.
- The package is intentionally a facade over split packages. Public APIs stay importable from `tigrbl.*`, while resident concepts are implemented in packages such as `tigrbl_core`, `tigrbl_canon`, `tigrbl_runtime`, `tigrbl_concrete`, `tigrbl_ops_oltp`, and engine plugins.
- Use the facade when you want one install and one import surface for API authoring, route mounting, docs emission, engine binding, and request execution.

## High-level feature and productization list

- Schema-first API construction from SQLAlchemy models, typed specs, Pydantic schemas, and canonical operation definitions.
- REST and JSON-RPC parity: the same operation specification can be exposed through REST routes and JSON-RPC methods, with OpenAPI and OpenRPC documentation surfaces carried by the concrete/system packages.
- Canonical operations: CRUD, bulk, analytical, realtime, stream, transfer, and datagram operation families are normalized through spec and canon packages before runtime execution.
- Phase lifecycle: request handling moves through explicit binding, parse, validation, authorization, pre-handler, handler, post-handler, transaction, response, and post-commit phases owned by the runtime/atom layers.
- Hook and dependency surfaces: model hooks, router hooks, REST deps, security dependencies (`secdeps`), anonymous-operation allowances, and engine context are first-class authoring inputs.
- Engine ecosystem: SQLite, PostgreSQL, in-memory, Redis, DuckDB, pandas, DataFrame, CSV, XLSX, PySpark, Snowflake, BigQuery, ClickHouse, cache, queue, pub/sub, Bloom, dedupe, key-value, LRU, and rate-limit packages are split as installable engine plugins.
- Native object model: concrete apps, routers, route wrappers, requests, responses, middleware, security schemes, docs builders, and engine providers are implemented as first-class package objects rather than hidden framework state.
- Benchmark positioning: Tigrbl is designed for schema-driven API generation and operation parity rather than hand-written route microframework ergonomics. Use `tigrbl_tests` for benchmark and parity surfaces when comparing Tigrbl and FastAPI style implementations.

## Tigrbl versus FastAPI benchmark context

- FastAPI is a hand-authored ASGI application framework. Tigrbl is a schema-first ASGI framework that derives public operations, docs, security metadata, and REST/JSON-RPC surfaces from model and operation specs.
- Benchmark comparisons should separate route dispatch overhead from generated-operation value: Tigrbl emphasizes fewer handwritten routes, consistent CRUD/bulk behavior, and documentation parity across transports.
- Place benchmark fixtures, reproducible examples, and FastAPI comparison scripts in `tigrbl_tests`, then link published benchmark evidence from the facade README when release evidence exists.

## Design-practice map

Tigrbl API design works best when each concern has a single package residence:

- Public API authoring belongs in the `tigrbl` facade: import `TigrblApp`, `TigrblRouter`, `TableBase`, decorators, security helpers, and schema/operation helpers from one place.
- Durable operation meaning belongs in [`tigrbl_core`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core): `OpSpec`, binding specs, hook specs, engine specs, request/response specs, `secdeps`, and schema contracts.
- Canonical operation discovery belongs in [`tigrbl_canon`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon): model/router/app collection, MRO merge, REST path planning, RPC method planning, and engine resolution.
- Runtime execution belongs in [`tigrbl_runtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_runtime): phase lifecycle, transaction handling, protocol atoms, response encoding, callback fences, and Rust bridge surfaces.
- Concrete ASGI objects belong in [`tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete): apps, routers, routes, requests, responses, middleware, dependencies, security objects, docs builders, and diagnostics.
- Backend-specific session, transaction, persistence, and database guard behavior belongs in the split `tigrbl_engine_*` packages.

Use the facade for productized application code. Use the split package READMEs when you need the resident semantics of a class, decorator, phase, operation family, engine, or guard.

## Terminology

| Term | Package residence | Meaning |
|------|-------------------|---------|
| Facade | `tigrbl` | Public authoring surface that keeps the split package graph importable from one package. |
| Table / model | `tigrbl`, `tigrbl_orm`, `tigrbl_core` | SQLAlchemy-backed resource definition and its portable table specification. |
| Operation | `tigrbl_core`, `tigrbl_canon`, `tigrbl_ops_*` | Verb-driven action such as `create`, `read`, `merge`, `query`, `stream`, or a custom operation. |
| Canon op | `tigrbl_canon` | Deterministic operation projection after decorators, inheritance, router/app inputs, bindings, hooks, and defaults are merged. |
| Binding | `tigrbl_core`, `tigrbl_canon` | REST, JSON-RPC, stream, SSE, WebSocket, or WebTransport exposure for an operation. |
| Hook | `tigrbl_core`, `tigrbl_concrete`, `tigrbl_runtime` | Callback attached to a phase such as `PRE_HANDLER`, `POST_HANDLER`, or `POST_COMMIT`. |
| Phase | `tigrbl_runtime`, `tigrbl_atoms` | Ordered runtime step where request parsing, validation, authorization, handlers, transactions, hooks, and response work occur. |
| Dependency | `tigrbl_concrete` | Callable injected into concrete routing or runtime execution. |
| Security dependency / `secdeps` | `tigrbl_core`, `tigrbl_concrete` | Operation-level security dependencies that also project OpenAPI security metadata. |
| Engine | `tigrbl_engine_*`, `tigrbl_concrete`, `tigrbl_runtime` | Backend session and transaction provider selected by application, router, model, or operation context. |
| Spec | `tigrbl_core`, `tigrbl_spec`, `tigrbl_rs_spec` | Portable description of apps, tables, operations, bindings, hooks, engines, requests, and responses. |

## Canonical operation design

Default OLTP operations are intentionally boring. They should map predictably to REST routes, JSON-RPC methods, input shapes, output shapes, and transaction behavior.

| Verb | REST route | JSON-RPC method | Scope | Request body | Result |
|------|------------|-----------------|-------|--------------|--------|
| `create` | `POST /{resource}` | `Model.create` | collection | object | object |
| `read` | `GET /{resource}/{id}` | `Model.read` | member | identifier | object |
| `update` | `PATCH /{resource}/{id}` | `Model.update` | member | partial object | object |
| `replace` | `PUT /{resource}/{id}` | `Model.replace` | member | full object | object |
| `merge` | `PATCH /{resource}/{id}` | `Model.merge` | member | merge object | object |
| `delete` | `DELETE /{resource}/{id}` | `Model.delete` | member | identifier | object |
| `list` | `GET /{resource}` | `Model.list` | collection | query object | array |
| `clear` | `DELETE /{resource}` | `Model.clear` | collection | filter object | object |
| `bulk_create` | `POST /{resource}` | `Model.bulk_create` | collection | array | array |
| `bulk_update` | `PATCH /{resource}` | `Model.bulk_update` | collection | array | array |
| `bulk_replace` | `PUT /{resource}` | `Model.bulk_replace` | collection | array | array |
| `bulk_merge` | `PATCH /{resource}` | `Model.bulk_merge` | collection | array | array |
| `bulk_delete` | `DELETE /{resource}` | `Model.bulk_delete` | collection | filter object | object |

Design guidance:

- Prefer default CRUD verbs for resource lifecycle work; add custom operations only when the operation is domain-specific.
- Treat REST and JSON-RPC as projections of the same operation, not separate implementations.
- Keep `update`, `replace`, and `merge` semantically distinct: `update` patches supplied fields, `replace` represents PUT-style replacement, and `merge` is for merge/upsert style behavior where the operation contract allows it.
- Avoid conflicting REST claims. `bulk_create` and `create` both want collection `POST`; `bulk_delete` and `clear` both want collection `DELETE`. Keep JSON-RPC methods available for operation parity when one REST route must win.
- Put transactional CRUD behavior in `tigrbl_ops_oltp`, analytical behavior in `tigrbl_ops_olap`, realtime behavior in `tigrbl_ops_realtime`, and backend persistence rules in the engine package.

## REST and JSON-RPC parity

The same table and operation definitions can produce REST and JSON-RPC surfaces. The authoring rule is: define the operation once, then let canon/runtime/concrete packages project it.

```python
from tigrbl import TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


class Widget(TableBase, GUIDPk):
    __tablename__ = "readme_widgets"

    name = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False), mount_system=False)
app.include_table(Widget)
app.initialize()
app.mount_jsonrpc(prefix="/rpc")
```

This pattern gives you a REST collection/member surface and a JSON-RPC method namespace from the same table operation set. Use [`tigrbl_canon`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon) to reason about why an operation is exposed, [`tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete) to inspect route and docs objects, and [`tigrbl_runtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_runtime) to inspect execution.

## Custom operations

Use `op_ctx` when a table, router, or app needs a domain-specific operation that is still visible to canon mapping, REST routing, JSON-RPC dispatch, docs generation, and runtime execution.

```python
from tigrbl import TigrblApp, op_ctx
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, Integer


class Health(TableBase):
    __tablename__ = "readme_health"

    id = Column(Integer, primary_key=True)

    @op_ctx(alias="ping", target="custom", http_methods=("GET",))
    def ping(cls, ctx):
        return {"status": "ok", "owner": cls.__name__}


app = TigrblApp(mount_system=False)
app.include_table(Health)
```

Design guidance:

- Give custom operations stable aliases; those aliases become documentation, routing, and RPC vocabulary.
- Use `target="custom"` for domain behavior that is not one of the canonical CRUD targets.
- Keep operation bodies small. Move persistence semantics into operation packages and engine-specific behavior into engine packages.

## Phase lifecycle and hooks

Tigrbl operations execute through named phases. Hooks should enforce policy, normalize inputs, add audit behavior, trigger side effects, or enrich context without hiding the core operation contract.

| Phase | Design purpose |
|-------|----------------|
| `PRE_TX_BEGIN` | Validate request context before transaction work begins. |
| `START_TX` | Open or attach a transaction/session. |
| `PRE_HANDLER` | Authorize, normalize, validate, and prepare handler inputs. |
| `HANDLER` | Execute the operation handler. |
| `POST_HANDLER` | Shape handler output while still inside transaction scope. |
| `PRE_COMMIT` | Run final checks before commit. |
| `END_TX` | Commit/rollback and close transaction scope. |
| `POST_COMMIT` | Run committed side effects before the response is finalized. |
| `POST_RESPONSE` | Run after-response work. |
| `ON_<PHASE>_ERROR` | Handle phase-specific failures. |
| `ON_ERROR` | General fallback error handling. |
| `ON_ROLLBACK` | Cleanup after rollback. |

```python
from tigrbl import hook_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


class AuditedWidget(TableBase, GUIDPk):
    __tablename__ = "readme_audited_widgets"

    name = Column(String, nullable=False)

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def normalize_create(cls, ctx):
        payload = ctx.get("payload") or {}
        if "name" in payload:
            payload["name"] = payload["name"].strip()
        ctx["payload"] = payload
```

Design guidance:

- Attach hooks where the behavior belongs: model hooks for model policy, router hooks for route-group policy, app hooks for application-wide policy.
- Prefer `PRE_HANDLER` for request normalization and authorization preparation.
- Prefer `POST_COMMIT` for committed side effects; avoid doing durable side effects before the transaction decision is known.
- Document non-obvious hooks in the package where the hook class or concept resides.

## Security dependencies and dependencies

Security dependencies should be declared as operation metadata when they are part of the public operation contract. This keeps runtime authorization and OpenAPI security metadata aligned.

```python
from tigrbl import HTTPBasic
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.security import Security
from tigrbl.types import Column, String


def basic_operator(
    credential=Security(HTTPBasic(scheme_name="BasicAuth", realm="operators")),
):
    return credential


class SecureWidget(TableBase, GUIDPk):
    __tablename__ = "readme_secure_widgets"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(alias="read", target="read", secdeps=(basic_operator,)),
    )
```

Design guidance:

- Use `secdeps` when security is part of the operation contract and should appear in docs.
- Use concrete dependencies for route/runtime plumbing that is not itself a security scheme.
- Keep security scheme objects in `tigrbl_concrete`/`tigrbl.security`; keep operation metadata in `tigrbl_core`.

## Engine selection and database guards

Engine selection should be explicit and close to the scope it affects.

```python
from tigrbl import TigrblApp, engine_ctx
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


@engine_ctx(kind="sqlite", mode="memory")
class LocalWidget(TableBase, GUIDPk):
    __tablename__ = "readme_local_widgets"

    name = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False), mount_system=False)
app.include_table(LocalWidget)
```

Design guidance:

- Put engine defaults at app/router scope when most tables share a backend.
- Put `engine_ctx` at model or operation scope when the backend choice is part of that resource or operation contract.
- Document database guard behavior in the engine README: connection lifecycle, transaction lifecycle, persistence boundary, local/remote credential expectations, durability assumptions, and cleanup behavior.

## Benchmark and parity execution

The facade README should explain benchmark intent; the executable benchmark harness lives in `tigrbl_tests`.

```bash
python pkgs/core/tigrbl_tests/benchmarks/run_hot_path_perf_suite.py --help
python -m pytest pkgs/core/tigrbl_tests/tests/perf/test_tigrbl_vs_fastapi_create_benchmark.py -q
```

Benchmark guidance:

- Compare generated-operation value, route parity, documentation parity, and runtime behavior separately from raw route dispatch.
- Keep published benchmark artifacts under `pkgs/core/tigrbl_tests/tests/perf/` or another governed evidence path, then link the evidence from this facade README.
- When reporting Tigrbl versus FastAPI results, state the transport, operation count, database mode, server, concurrency model, and whether the comparison measures REST, JSON-RPC, streaming, SSE, WebSocket, or WebTransport.

## Package ecosystem cross-links

Core cross-links:
- [`tigrbl`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl) - Facade package
- [`tigrbl_core`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_core) - Spec and primitive contracts
- [`tigrbl_canon`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_canon) - Canonical mapping and operation resolution
- [`tigrbl_runtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_runtime) - Phase lifecycle and execution runtime
- [`tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete) - Native objects, transports, hooks, deps, and secdeps
- [`tigrbl_ops_oltp`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_oltp) - CRUD and transactional operation handlers
- [`tigrbl_ops_olap`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_olap) - Analytical operation boundary
- [`tigrbl_ops_realtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_ops_realtime) - Stream, transfer, datagram, and realtime ops
- [`tigrbl_tests`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_tests) - Examples, benchmark, parity, and package test surfaces
Engine cross-links:
- [`tigrbl_engine_sqlite`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_sqlite) - SQLite local transactional engine
- [`tigrbl_engine_postgres`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_postgres) - PostgreSQL SQLAlchemy engine
- [`tigrbl_engine_inmemory`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_inmemory) - Process-local transactional in-memory engine
- [`tigrbl_engine_redis`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_redis) - Redis cache/database engine
- [`tigrbl_engine_duckdb`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_duckdb) - DuckDB analytical engine
- [`tigrbl_engine_pandas`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_pandas) - pandas DataFrame engine
- [`tigrbl_engine_pgsqli_wal`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/engines/tigrbl_engine_pgsqli_wal) - PostgreSQL and SQLite WAL engine
Rust cross-links:
- [`tigrbl_rs_spec`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_spec) - Rust IR and AppSpec model
- [`tigrbl_rs_atoms`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_atoms) - Rust atom catalog and phase algebra
- [`tigrbl_rs_kernel`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_kernel) - Rust compiler and plan optimizer
- [`tigrbl_rs_runtime`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_runtime) - Rust executor and callback fences
- [`tigrbl_rs_ports`](https://github.com/tigrbl/tigrbl/tree/master/crates/tigrbl_rs_ports) - Engine, session, transaction, callback, and handler ports

## Install

```bash
pip install tigrbl
```

## Package discovery

Search and AI discovery terms for `tigrbl` include: tigrbl, ASGI, REST, JSON-RPC, SQLAlchemy, Pydantic, asgi, api, json-rpc, rest, sqlalchemy, pydantic, api-framework.

## Package-local entry point

This file is a package-local distribution entry point.
It is not the authoritative location for repository governance, current target status, current state reporting, certification claims, or release evidence.

## Canonical repository docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

## Package identity

- canonical repository: `https://github.com/tigrbl/tigrbl`
- organization: `https://github.com/tigrbl`
- social: `https://discord.gg/K4YTAPapjR`
- package path: `https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl`
- workspace path: `pkgs/core/tigrbl`
- workspace class: core Python package
- implementation layout: `tigrbl/`

Long-form repository documentation is governed from `docs/`.
