<div align="center">
<h1>tigrbl</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Schema-first ASGI framework for REST and JSON-RPC APIs with OpenAPI, OpenRPC, SQLAlchemy, typed validation, hooks, and engine plugins.</strong></p>
<a href="https://pypi.org/project/tigrbl/"><img src="https://img.shields.io/pypi/v/tigrbl?label=PyPI" alt="PyPI version for tigrbl"/></a>
<a href="https://pypi.org/project/tigrbl/"><img src="https://static.pepy.tech/badge/tigrbl" alt="Downloads for tigrbl"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl/README.md.svg?label=hits" alt="Repository hits for tigrbl README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl"/></a>
</div>

## What is tigrbl?

Schema-first ASGI framework for REST and JSON-RPC APIs with OpenAPI, OpenRPC, SQLAlchemy, typed validation, hooks, and engine plugins.

## Why use tigrbl?

Use it when you want the public Tigrbl authoring surface in one install target instead of composing split packages by hand.

## When should I install tigrbl?

Install it for application projects, examples, service skeletons, and teams that want REST, JSON-RPC, docs, schemas, engines, and CLI support from one facade.

## Who is tigrbl for?

Application developers, platform teams, and service owners building schema-first Python APIs.

## Where does tigrbl fit?

`tigrbl` lives at `pkgs/core/tigrbl` and serves schema-first service authoring, REST and JSON-RPC projection, docs, engines, and CLI workflows.

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
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

## What It Owns

`tigrbl` owns the `public facade package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl`: __main__, canonical_json, cli, config/, ddl/, decorators/, engine/, factories/, hook/, middlewares/, op/, orm/

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

## How To Choose This Package

Choose `tigrbl` when you want the full public facade: app composition, schema-first routing, REST and JSON-RPC projection, docs generation, engine integration, and CLI workflow. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) only when you are building framework extensions or testing a specific internal boundary.

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
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/core/tigrbl](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl).

## Package-local Boundary

This README is the package-local distribution entry point for `tigrbl`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
