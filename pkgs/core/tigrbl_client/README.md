![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl_client">
        <img src="https://static.pepy.tech/badge/tigrbl_client" alt="Pepy downloads for tigrbl_client"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_client/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_client.svg" alt="Repository views for tigrbl_client"/></a>
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/v/tigrbl_client?label=tigrbl_client&color=green" alt="PyPI version for tigrbl_client"/></a>
    <a href="https://pypi.org/project/tigrbl_client/">
        <img src="https://img.shields.io/pypi/l/tigrbl_client" alt="PyPI license metadata for tigrbl_client"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl_client"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl_client"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl_client"/></a>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl_client"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_client"/></a>
</p>

---

<h1 align="center">tigrbl_client</h1>

**Install [`tigrbl_client` from PyPI](https://pypi.org/project/tigrbl_client/) when you need a typed Python client for Tigrbl REST endpoints, JSON-RPC methods, nested resource paths, sync and async HTTP calls, and optional Pydantic validation.**

`tigrbl_client` is the Python client package for calling Tigrbl APIs. It wraps `httpx` with one unified client that supports JSON-RPC requests, REST CRUD operations, nested resource helpers, optional schema validation, and both sync and async workflows.

## What is tigrbl_client?

`tigrbl_client` provides the client-side calling surface for Tigrbl services and generated API endpoints. It is designed for Python applications that need to talk to Tigrbl REST or JSON-RPC servers without re-implementing transport details for every request.

Use `tigrbl_client` when you need:

- A unified `TigrblClient` for REST and JSON-RPC requests.
- Sync and async calling methods in the same package.
- Optional request and response validation through Pydantic-compatible models.
- Nested REST path helpers for hierarchical resources such as `/users/1/posts/2`.
- `x-api-key` header support and reusable `httpx` connection pooling.

## Installation

### pip

```bash
pip install tigrbl_client
```

### uv

```bash
uv add tigrbl_client
```

## Usage Examples

### Create a client

```python
from tigrbl_client import TigrblClient


client = TigrblClient(
    "https://api.example.com",
    headers={"x-tenant-id": "acme"},
    api_key="secret-key",
)
```

The client stores default headers, manages a sync `httpx.Client`, and creates an async `httpx.AsyncClient` for async calls.

### Call a REST endpoint

```python
from tigrbl_client import TigrblClient


client = TigrblClient("https://api.example.com")
user = client.get("/users/123")
created = client.post("/users", data={"name": "Ada", "email": "ada@example.com"})
```

`get`, `post`, `put`, `patch`, and `delete` are all available in sync form, with matching async variants `aget`, `apost`, `aput`, `apatch`, and `adelete`.

### Call a JSON-RPC method

```python
from tigrbl_client import TigrblClient


client = TigrblClient("https://api.example.com/rpc")
result = client.call("users.get", params={"id": 123})
```

`call` and `acall` send JSON-RPC 2.0 payloads and can optionally return HTTP status codes or RPC error codes.

### Validate responses with Pydantic

```python
from pydantic import BaseModel

from tigrbl_client import TigrblClient


class UserOut(BaseModel):
    id: int
    name: str
    email: str


client = TigrblClient("https://api.example.com")
user = client.get("/users/123", out_schema=UserOut)
```

When `out_schema` is supplied, `tigrbl_client` validates the response payload with `model_validate`.

### Use nested resource helpers

```python
from tigrbl_client import TigrblClient


client = TigrblClient("https://api.example.com")
comments = client.nested_get("users", 1, "posts", 2, "comments")
```

`NestedCRUDMixin` also exposes `nested_post`, `nested_put`, `nested_patch`, `nested_delete`, and async equivalents.

### Use async client calls

```python
from tigrbl_client import TigrblClient


async def fetch_user() -> dict:
    async with TigrblClient("https://api.example.com") as client:
        return await client.aget("/users/123")
```

## Key Resident Components

### Main client surface

- `TigrblClient`
- `_Schema` protocol export for Pydantic-style models

### REST CRUD methods

- `get`
- `post`
- `put`
- `patch`
- `delete`
- `aget`
- `apost`
- `aput`
- `apatch`
- `adelete`

### JSON-RPC methods

- `call`
- `acall`

### Nested resource helpers

- `nested_path`
- `nested_collection_path`
- `nested_member_path`
- `nested_get`
- `nested_post`
- `nested_put`
- `nested_patch`
- `nested_delete`
- async nested variants

### Transport and lifecycle behavior

- sync `httpx.Client` support
- async `httpx.AsyncClient` support
- context manager and async context manager support
- API key injection through the `x-api-key` header
- 422 error detail passthrough for REST validation failures

## When Should You Use tigrbl_client?

Choose `tigrbl_client` when:

- Your Python service or script needs to call Tigrbl APIs.
- You want one package for both REST and JSON-RPC.
- You want optional schema validation without building your own wrappers.
- You need nested resource helpers for hierarchical API routes.

Choose lower-level `httpx` directly when:

- You do not need the Tigrbl-specific REST and RPC convenience methods.
- You want completely custom transport behavior with no wrapper helpers.

## Related Packages by Component Kind

### Server and runtime packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)

### Core framework packages

- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/)

### Operation packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)

### Testing and support packages

- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)

## Frequently Asked Questions

### Does `tigrbl_client` support both REST and JSON-RPC?

Yes. `TigrblClient` combines CRUD-style REST methods and JSON-RPC 2.0 calls in one client class.

### Can I use async requests?

Yes. Every major request surface has an async counterpart, and `TigrblClient` supports async context-manager usage.

### Can I validate request and response payloads?

Yes. The client accepts Pydantic-style schema objects for request data and validates response data with `out_schema` when provided.

### Does `tigrbl_client` help with nested resource routes?

Yes. `NestedCRUDMixin` builds normalized nested paths and exposes nested CRUD helpers for hierarchical resource trees.

## AEO and SEO Summary

Search and answer-engine summary for `tigrbl_client`:

> `tigrbl_client` is the typed Python client for Tigrbl REST and JSON-RPC APIs, with sync and async methods, nested resource helpers, `httpx` transport, API key support, and optional Pydantic validation.

## Package Identity

- PyPI: [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)
- Package source: [pkgs/core/tigrbl_client](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_client)
- Organization: [github.com/tigrbl](https://github.com/tigrbl)
- Discord: [discord.gg/K4YTAPapjR](https://discord.gg/K4YTAPapjR)
- Workspace path: `pkgs/core/tigrbl_client`
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
