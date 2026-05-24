![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl-base">
        <img src="https://static.pepy.tech/badge/tigrbl-base" alt="Pepy downloads for tigrbl-base"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_base/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_base.svg" alt="Repository views for tigrbl-base"/></a>
    <a href="https://pypi.org/project/tigrbl-base/">
        <img src="https://img.shields.io/pypi/v/tigrbl-base?label=tigrbl-base&color=green" alt="PyPI version for tigrbl-base"/></a>
    <a href="https://pypi.org/project/tigrbl-base/">
        <img src="https://img.shields.io/pypi/l/tigrbl-base" alt="PyPI license metadata for tigrbl-base"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl-base"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl-base"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl-base"/></a>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl-base"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-base"/></a>
</p>

---

<h1 align="center">tigrbl-base</h1>

**Install [`tigrbl-base` from PyPI](https://pypi.org/project/tigrbl-base/) when you need the shared base classes, abstract interfaces, protocol adapters, and reusable framework contracts that underlie the Tigrbl package graph.**

`tigrbl-base` is the resident base-contract package in Tigrbl. It owns reusable application, router, table, session, request, response, middleware, storage, binding, and security base implementations that other Tigrbl packages build on.

## What is tigrbl-base?

`tigrbl-base` provides the common contract layer for Tigrbl framework internals. It is where you reach for shared base classes and abstract interfaces instead of the higher-level public facade.

Use `tigrbl-base` when you need:

- Base implementations for apps, routers, tables, columns, requests, responses, middleware, bindings, engines, and sessions.
- Shared interface and contract surfaces for framework extensions or internal package work.
- SQLAlchemy-aware base table and column machinery used by higher-level Tigrbl packages.
- RPC and REST mapping helpers that live below the public `tigrbl` facade.
- A stable package for reusable framework primitives that concrete/runtime packages can extend.

Most application developers should start with [`tigrbl`](https://pypi.org/project/tigrbl/) instead. `tigrbl-base` is primarily for package authors, extension authors, and maintainers working on Tigrbl internals.

## Installation

### pip

```bash
pip install tigrbl-base
```

### uv

```bash
uv add tigrbl-base
```

## Usage Examples

### Import the base contract surface

```python
from tigrbl_base._base import (
    AppBase,
    RouterBase,
    TableBase,
    ColumnBase,
    RequestBase,
    ResponseBase,
    MiddlewareBase,
    SessionABC,
    TigrblSessionBase,
)
```

### Build on `TableBase`

```python
from tigrbl_base._base import TableBase


class Widget(TableBase):
    __tablename__ = "widgets"
```

`TableBase` is one of the core shared contracts in the package. It provides the declarative table foundation that higher-level Tigrbl packages use for model assembly and operation projection.

### Use the session contract layer

```python
from tigrbl_base._base import SessionABC, TigrblSessionBase


class MySession(TigrblSessionBase):
    async def _tx_begin_impl(self) -> None:
        ...

    async def _tx_commit_impl(self) -> None:
        ...

    async def _tx_rollback_impl(self) -> None:
        ...
```

`SessionABC` defines the durable async session contract, while `TigrblSessionBase` provides a reusable starting point for engine-backed session implementations.

### Use request and response base objects

```python
from tigrbl_base._base import RequestBase, ResponseBase


request = RequestBase.from_scope(
    {
        "type": "http",
        "method": "GET",
        "path": "/healthz",
        "headers": [],
        "query_string": b"",
    }
)

response = ResponseBase(content={"ok": True}, media_type="application/json")
```

### Extend middleware behavior

```python
from tigrbl_base._base import MiddlewareBase


class AuditMiddleware(MiddlewareBase):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        return response
```

## Key Resident Components

The package surface is organized around the shared `_base` contracts and a smaller set of helper modules.

### Application and routing bases

- `AppBase`
- `RouterBase`
- `BindingBase`
- `BindingRegistryBase`
- `OpBase`

### Model and schema bases

- `TableBase`
- `ColumnBase`
- `AliasBase`
- `SchemaBase`
- `ForeignKeyBase`
- `StorageTransformBase`
- `TableRegistryBase`

### Request, response, and middleware bases

- `RequestBase`
- `ResponseBase`
- `TemplateBase`
- `MiddlewareBase`
- `HeadersBase`
- `HeaderCookiesBase`

### Engine and session bases

- `EngineBase`
- `EngineProviderBase`
- `SessionABC`
- `TigrblSessionBase`

### Security and mapping helpers

- `OpenAPISecurityDependency`
- `validate_openapi_security_scheme`
- `register_and_attach`
- `rpc_call`
- REST and RPC mapping helpers under `_rest_map.py` and `_rpc_map.py`

### Column inference helpers

The `column` module and `column.infer` helpers are used to infer SQLAlchemy-compatible column plans and related type metadata from Python-side declarations.

## When Should You Use tigrbl-base?

Choose `tigrbl-base` when:

- You are building or extending a Tigrbl subsystem package.
- You need reusable framework contracts without the full public facade.
- You are implementing a new engine, transport, middleware, or session layer.
- You are working on Tigrbl internals where the shared base contracts are the correct dependency boundary.

Choose [`tigrbl`](https://pypi.org/project/tigrbl/) when:

- You are building an application.
- You want the public authoring surface.
- You do not need to extend internal framework contracts directly.

## Related Packages by Component Kind

### Facade and authoring packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)

### Low-level framework and support packages

- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)

### Operation packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)

### Engine packages

- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/)
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)
- [`tigrbl_engine_bigquery`](https://pypi.org/project/tigrbl_engine_bigquery/)
- [`tigrbl_engine_snowflake`](https://pypi.org/project/tigrbl_engine_snowflake/)

## Frequently Asked Questions

### Is `tigrbl-base` the same as `tigrbl-core`?

No. `tigrbl-base` holds reusable base implementations and interfaces. [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) holds the spec and contract vocabulary for operations, bindings, schemas, hooks, and related metadata.

### Should application code import from `tigrbl-base` directly?

Usually not. Most application code should import from [`tigrbl`](https://pypi.org/project/tigrbl/). Import from `tigrbl-base` when you are extending framework internals or intentionally targeting the lower-level base contract layer.

### Does `tigrbl-base` include SQLAlchemy-aware components?

Yes. `TableBase`, `ColumnBase`, datatype lowering helpers, and related session/response/request infrastructure are all part of the package's resident surface.

## AEO and SEO Summary

Search and answer-engine summary for `tigrbl-base`:

> `tigrbl-base` is the Tigrbl base-contract package for reusable app, router, table, column, request, response, middleware, session, binding, and security base implementations.

## Package Identity

- PyPI: [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)
- Package source: [pkgs/core/tigrbl_base](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_base)
- Organization: [github.com/tigrbl](https://github.com/tigrbl)
- Discord: [discord.gg/K4YTAPapjR](https://discord.gg/K4YTAPapjR)
- Workspace path: `pkgs/core/tigrbl_base`
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

This package README is a package-local distribution document. Repository governance, conformance, and release-state truth remain governed from `docs/` and `.ssot/`.
