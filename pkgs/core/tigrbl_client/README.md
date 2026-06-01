<div align="center">
<h1>tigrbl_client</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Typed Python client for Tigrbl REST and JSON-RPC APIs with sync and async calls, nested resource helpers, and optional Pydantic validation.</strong></p>
<a href="https://pypi.org/project/tigrbl_client/"><img src="https://img.shields.io/pypi/v/tigrbl_client?label=PyPI" alt="PyPI version for tigrbl_client"/></a>
<a href="https://pypi.org/project/tigrbl_client/"><img src="https://static.pepy.tech/badge/tigrbl_client" alt="Downloads for tigrbl_client"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl_client"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_client/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_client/README.md.svg?label=hits" alt="Repository hits for tigrbl_client README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl_client"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl_client"/></a>
</div>

## What is tigrbl_client?

Typed Python client for Tigrbl REST and JSON-RPC APIs with sync and async calls, nested resource helpers, and optional Pydantic validation.

## Why use tigrbl_client?

Use it when a Python service or test suite needs a typed client for Tigrbl REST and JSON-RPC APIs.

## When should I install tigrbl_client?

Install it in consumers, integration tests, SDK adapters, and automation that calls an already-running Tigrbl service.

## Who is tigrbl_client for?

Client authors, API consumers, QA engineers, and service integration teams.

## Where does tigrbl_client fit?

`tigrbl_client` lives at `pkgs/core/tigrbl_client` and serves calling Tigrbl services from Python clients and tests.

## How does tigrbl_client work?

It wraps HTTP calls with sync and async helpers, optional API-key headers, REST CRUD helpers, JSON-RPC calls, and nested-resource helpers.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl_client
```

```bash
pip install tigrbl_client
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_client`](https://pypi.org/project/tigrbl_client/) |
| Repository path | [`pkgs/core/tigrbl_client`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_client) |
| Python import root | `tigrbl_client` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl_client` owns the `client package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_client`: _crud, _nested_crud, _rpc

## Public API and Import Surface

- Import roots: `tigrbl_client`.
- Public symbols: `NestedCRUDMixin`, `TigrblClient`, `_Schema`.
- Workspace dependencies: none declared.
- External runtime dependencies: `fastapi>=0.100.0`, `pydantic>=2.0.0`.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl_client
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_client"))
PY
```

### Call REST endpoints

```python
from tigrbl_client import TigrblClient

with TigrblClient("https://api.example.com") as client:
    item = client.get("/items/1")
    created = client.post("/items", data={"name": "example"})
```

### Call JSON-RPC endpoints

```python
from tigrbl_client import TigrblClient

client = TigrblClient("https://api.example.com/rpc")
result = client.call("items.get", params={"id": 1})
```

### Use async helpers

```python
from tigrbl_client import TigrblClient

async with TigrblClient("https://api.example.com") as client:
    item = await client.aget("/items/1")
```

## How To Choose This Package

Choose `tigrbl_client` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/core/tigrbl_client](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_client).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl_client`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
