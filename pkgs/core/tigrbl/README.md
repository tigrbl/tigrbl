![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl">
        <img src="https://static.pepy.tech/badge/tigrbl" alt="Pepy downloads for tigrbl"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl.svg" alt="Repository views for tigrbl"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/v/tigrbl?label=tigrbl&color=green" alt="PyPI version for tigrbl"/></a>
    <a href="https://pypi.org/project/tigrbl/">
        <img src="https://img.shields.io/pypi/l/tigrbl" alt="PyPI license metadata for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl"/></a>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl"/></a>
</p>
---

<h1 align="center">Tigrbl</h1>

**Install [`tigrbl` from PyPI](https://pypi.org/project/tigrbl/) when you want one Python package that exposes the public Tigrbl authoring surface for schema-first REST APIs, JSON-RPC APIs, OpenAPI, OpenRPC, SQLAlchemy models, typed validation, hooks, and engine plugins.**

`tigrbl` is the facade package in the Tigrbl Python package graph. It re-exports the author-facing objects developers use first, while the underlying semantics stay resident in the split core, runtime, concrete, operation, and engine packages.

## What is Tigrbl?

Tigrbl is a schema-first ASGI API framework for building REST and JSON-RPC services from SQLAlchemy models, typed operation specs, documented bindings, and explicit runtime phases. Instead of hand-writing every route separately, you define tables, operations, hooks, bindings, and engine context once, then let Tigrbl project those definitions into API surfaces and documentation.

Use `tigrbl` when you want:

- A public facade import surface centered on `TigrblApp`, `TigrblRouter`, `TableBase`, `Column`, `op_ctx`, `hook_ctx`, `schema_ctx`, `engine_ctx`, and system docs builders.
- REST and JSON-RPC parity from the same underlying operation model.
- OpenAPI and OpenRPC generation from the same application graph.
- Explicit runtime phases for validation, authorization, handler execution, transactions, and post-commit work.
- Installable backend plugins for SQLite, PostgreSQL, Redis, DuckDB, pandas, BigQuery, Snowflake, ClickHouse, XLSX, and in-memory workloads.

## Installation

### pip

```bash
pip install tigrbl
```

### uv

```bash
uv add tigrbl
```

### Optional extras

```bash
pip install "tigrbl[postgres]"
pip install "tigrbl[servers]"
pip install "tigrbl[templates]"
pip install "tigrbl[tests]"
```

## Quickstart

```python
from tigrbl import TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


class Widget(TableBase, GUIDPk):
    __tablename__ = "widgets"

    name = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False), mount_system=False)
app.include_table(Widget)
app.initialize()
app.mount_jsonrpc(prefix="/rpc")
```

This gives you:

- A schema-first table model.
- Generated REST collection and member routes.
- Generated JSON-RPC methods from the same operation set.
- A single ASGI app surface that can emit OpenAPI, OpenRPC, and related docs.

## Usage Patterns

### Build a schema-first REST and JSON-RPC API

Tigrbl’s default authoring flow is:

1. Define tables and fields with SQLAlchemy-backed model classes.
2. Attach canonical or custom operations.
3. Bind engines, hooks, schemas, and security metadata.
4. Mount REST, JSON-RPC, OpenAPI, OpenRPC, and UI surfaces from the same graph.

### Add a custom operation

```python
from tigrbl import TigrblApp, op_ctx
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, Integer


class Health(TableBase):
    __tablename__ = "health"

    id = Column(Integer, primary_key=True)

    @op_ctx(alias="ping", target="custom", http_methods=("GET",))
    def ping(cls, ctx):
        return {"status": "ok", "owner": cls.__name__}


app = TigrblApp(mount_system=False)
app.include_table(Health)
```

### Add hook-driven normalization

```python
from tigrbl import hook_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


class AuditedWidget(TableBase, GUIDPk):
    __tablename__ = "audited_widgets"

    name = Column(String, nullable=False)

    @hook_ctx(ops="create", phase="PRE_HANDLER")
    def normalize_create(cls, ctx):
        payload = ctx.get("payload") or {}
        if "name" in payload:
            payload["name"] = payload["name"].strip()
        ctx["payload"] = payload
```

### Bind an engine explicitly

```python
from tigrbl import TigrblApp, engine_ctx
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, String


@engine_ctx(kind="sqlite", mode="memory")
class LocalWidget(TableBase, GUIDPk):
    __tablename__ = "local_widgets"

    name = Column(String, nullable=False)


app = TigrblApp(engine=mem(async_=False), mount_system=False)
app.include_table(LocalWidget)
```

## CLI Usage

The package ships the unified `tigrbl` CLI entry point.

```bash
tigrbl --help
tigrbl run myapp:app
tigrbl serve myapp:app --server uvicorn --host 127.0.0.1 --port 8000
tigrbl openapi myapp:app
tigrbl openrpc myapp:app
tigrbl routes myapp:app
tigrbl doctor myapp:app
tigrbl capabilities
```

Supported server targets in the current CLI surface:

- `tigrcorn`
- `uvicorn`
- `hypercorn`
- `gunicorn`

## Key Features

- Schema-first API design for SQLAlchemy-backed services.
- REST and JSON-RPC parity from one operation graph.
- OpenAPI and OpenRPC generation from the same application definition.
- Canonical operation families for CRUD, bulk, analytical, and realtime work.
- Runtime phases for parse, validation, authorization, handler execution, transactions, response shaping, and post-commit behavior.
- Hook surfaces for model, router, and app-level policy.
- Security dependencies that stay aligned with runtime auth and API docs.
- A facade import surface over split installable packages.

## Public API Surface

The facade re-exports the author-facing objects most users start with:

- `TigrblApp`
- `TigrblRouter`
- `TableBase`
- `Column`
- `Depends`
- `HTTPException`
- `op_ctx`
- `hook_ctx`
- `schema_ctx`
- `engine_ctx`
- `allow_anon`
- `HTTPBasic`
- `HTTPBearer`
- `OAuth2`
- `OpenIdConnect`
- `mount_diagnostics`

## How the Package Graph Is Split

Use the facade package for application authoring. Use the split packages when you need the resident semantics of a subsystem:

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) for operation specs, binding specs, schema contracts, and protocol metadata.
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/) for canonical operation discovery, route planning, and graph normalization.
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/) for concrete apps, routers, routes, requests, responses, middleware, and docs objects.
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) for runtime phases, execution flow, and transaction orchestration.
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/) for SQLAlchemy-backed tables, mixins, and persistence helpers.
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/) for transactional CRUD and bulk operation behavior.
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/) for analytical operation behavior.
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/) for streaming, websocket, and realtime operation behavior.

## Related Tigrbl Packages

### Core framework packages

- [`tigrbl`](https://pypi.org/project/tigrbl/) - Public facade package for the Tigrbl framework.
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/) - Runtime atom utilities and transport helpers.
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/) - Abstract base interfaces and shared framework contracts.
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/) - Canonical mapping, route planning, and symbol resolution.
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/) - Concrete ASGI objects, routes, middleware, responses, and docs surfaces.
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) - Core specs, decorators, schemas, hooks, and operation primitives.
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/) - Kernel orchestration and runtime plan composition.
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/) - ORM tables, mixins, columns, and persistence helpers.
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) - Runtime pipeline and execution surfaces.
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/) - Shared typing aliases, protocols, and generics.
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/) - Typed client helpers for Tigrbl APIs.
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/) - Shared specification artifacts and compatibility targets.
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) - Test fixtures, conformance helpers, and benchmark surfaces.

### Operation packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/) - Transactional CRUD and bulk operation handlers.
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/) - Analytical and query-oriented operation surfaces.
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/) - Realtime, stream, websocket, and event operation surfaces.

### Engine packages

- [`tigrbl_engine_bigquery`](https://pypi.org/project/tigrbl_engine_bigquery/)
- [`tigrbl_engine_clickhouse`](https://pypi.org/project/tigrbl_engine_clickhouse/)
- [`tigrbl_engine_csv`](https://pypi.org/project/tigrbl_engine_csv/)
- [`tigrbl_engine_dataframe`](https://pypi.org/project/tigrbl_engine_dataframe/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_inmemcache`](https://pypi.org/project/tigrbl_engine_inmemcache/)
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/)
- [`tigrbl_engine_membloom`](https://pypi.org/project/tigrbl_engine_membloom/)
- [`tigrbl_engine_memdedupe`](https://pypi.org/project/tigrbl_engine_memdedupe/)
- [`tigrbl_engine_memkv`](https://pypi.org/project/tigrbl_engine_memkv/)
- [`tigrbl_engine_memlru`](https://pypi.org/project/tigrbl_engine_memlru/)
- [`tigrbl_engine_mempubsub`](https://pypi.org/project/tigrbl_engine_mempubsub/)
- [`tigrbl_engine_memqueue`](https://pypi.org/project/tigrbl_engine_memqueue/)
- [`tigrbl_engine_memrate`](https://pypi.org/project/tigrbl_engine_memrate/)
- [`tigrbl_engine_numpy`](https://pypi.org/project/tigrbl_engine_numpy/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)
- [`tigrbl_engine_pgsqli_wal`](https://pypi.org/project/tigrbl_engine_pgsqli_wal/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_pyspark`](https://pypi.org/project/tigrbl_engine_pyspark/)
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/)
- [`tigrbl_engine_rediscachethrough`](https://pypi.org/project/tigrbl_engine_rediscachethrough/)
- [`tigrbl_engine_snowflake`](https://pypi.org/project/tigrbl_engine_snowflake/)
- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_xlsx`](https://pypi.org/project/tigrbl_engine_xlsx/)

### Application packages

- [`tigrbl_acme_ca`](https://pypi.org/project/tigrbl_acme_ca/)
- [`tigrbl_spiffe`](https://pypi.org/project/tigrbl_spiffe/)

## Frequently Asked Questions

### Is Tigrbl a REST framework or a JSON-RPC framework?

Both. Tigrbl is a schema-first ASGI framework that can project the same operation definitions into REST routes and JSON-RPC methods.

### Does Tigrbl generate OpenAPI and OpenRPC?

Yes. The public facade includes system documentation builders and mount helpers for OpenAPI, Swagger-style UI surfaces, OpenRPC, and Lens-style docs views.

### Is Tigrbl only for SQL databases?

No. Tigrbl supports SQLAlchemy-backed persistence and also ships installable engine packages for in-memory, Redis, analytics, warehouse, and tabular backends.

### When should I install `tigrbl` instead of a split package directly?

Install `tigrbl` when you want the public authoring surface in one dependency. Install the split packages directly when you need a narrower subsystem contract or you are extending a specific component kind.

## Benchmark and Comparison Guidance

Tigrbl is optimized for schema-driven API generation, operation parity, and documentation consistency. Benchmark comparisons against hand-authored frameworks should separate:

- Route dispatch overhead.
- Generated operation value.
- Documentation parity.
- Database mode and engine configuration.
- Transport type such as REST, JSON-RPC, SSE, WebSocket, or WebTransport.

For executable benchmark and parity assets, use [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/).

## Package Discovery Summary

Search and answer-engine summary for `tigrbl`:

> `tigrbl` is a schema-first ASGI API framework for REST, JSON-RPC, OpenAPI, OpenRPC, SQLAlchemy models, typed validation, hooks, runtime phases, and installable engine plugins.

## Package Identity

- PyPI: [`tigrbl`](https://pypi.org/project/tigrbl/)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)
- Package source: [pkgs/core/tigrbl](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl)
- Organization: [github.com/tigrbl](https://github.com/tigrbl)
- Discord: [discord.gg/K4YTAPapjR](https://discord.gg/K4YTAPapjR)
- Workspace path: `pkgs/core/tigrbl`
- Workspace class: core Python package

## Canonical Repository Docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

This package README is a package-local distribution document. Long-form repository governance, conformance, and release state remain governed from `docs/` and `.ssot/`.
