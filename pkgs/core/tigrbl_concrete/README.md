<div align="center">
<h1>tigrbl-concrete</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.</strong></p>
<a href="https://pypi.org/project/tigrbl-concrete/"><img src="https://img.shields.io/pypi/v/tigrbl-concrete?label=PyPI" alt="PyPI version for tigrbl-concrete"/></a>
<a href="https://pypi.org/project/tigrbl-concrete/"><img src="https://static.pepy.tech/badge/tigrbl-concrete" alt="Downloads for tigrbl-concrete"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-concrete"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_concrete/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_concrete/README.md.svg?label=hits" alt="Repository hits for tigrbl-concrete README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-concrete"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-concrete"/></a>
</div>

## What is tigrbl-concrete?

Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.

## Why use tigrbl-concrete?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-concrete?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-concrete for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-concrete fit?

`tigrbl-concrete` lives at `pkgs/core/tigrbl_concrete` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-concrete work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-concrete
```

```bash
pip install tigrbl-concrete
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/) |
| Repository path | [`pkgs/core/tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete) |
| Python import root | `tigrbl_concrete` |
| Console scripts | none declared |
| Entry points | `tigrbl.engine_plugins` |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

## What It Owns

`tigrbl-concrete` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_concrete`: _concrete/, _decorators/, _mapping/, ddl/, decorators, engine/, factories/, resolve/, security/, shortcuts/, system/, transport/

Package catalog:
- `tigrbl_concrete/_concrete/`: concrete app, router, route, table, column, operation, schema, request, response, headers, body, middleware, background, storage, session, binding, engine, and security classes/adapters.
- `tigrbl_concrete/_concrete/_security/`: API key, HTTP Basic, HTTP Bearer, mutual TLS, OAuth2, and OpenID Connect security primitives.
- `tigrbl_concrete/_decorators/` and `tigrbl_concrete/decorators.py`: concrete decorator implementations that attach engine, hook, op, response, schema, session, middleware, allow-anon, and related metadata.
- `tigrbl_concrete/_mapping/`: app, router, model, column, operation, core, and app-spec lowering helpers that turn specs and model metadata into concrete registrations.
- `tigrbl_concrete/engine/`: engine builders, binding, capability declarations, plugin discovery, registry, resolver, and collection helpers.
- `tigrbl_concrete/factories/` and `tigrbl_concrete/shortcuts/`: concrete app and REST shortcut helpers consumed by the facade.
- `tigrbl_concrete/resolve/`: handler resolution helpers.
- `tigrbl_concrete/security/`: concrete security dependency helpers.
- `tigrbl_concrete/system/diagnostics`: `/system/healthz`, `/system/hookz`, `/system/kernelz`, `/system/methodz`, and diagnostic router helpers.
- `tigrbl_concrete/system/docs`: OpenAPI, OpenRPC, JSON Schema, Swagger, lens, runtime-ops, and surface documentation helpers.
- `tigrbl_concrete/transport/rest` and `tigrbl_concrete/transport/jsonrpc`: REST route aggregation and JSON-RPC helper/model utilities.
- `tigrbl_concrete/ddl/` and `tigrbl_concrete/system/static`/`favicon`: DDL and static/docs support surfaces.

## Public API and Import Surface

- Import roots: `tigrbl_concrete`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `orjson`, `pydantic>=2.0`, `sqlalchemy`, `uvicorn`.

## Concrete Implementation Semantics

`tigrbl-concrete` is where abstract specs and base contracts become usable Python framework objects. It is intentionally below the `tigrbl` facade and above the atom/kernel/runtime internals. Application developers normally import through `tigrbl`; extension authors import this package when they need concrete classes, decorators, engine resolution, docs mounting, or diagnostics without taking the facade dependency.

The package performs four broad jobs:

- Lower core specs and base contracts into concrete app/router/table/operation objects.
- Register REST and JSON-RPC projections for model operations.
- Resolve engines, handlers, schemas, responses, security dependencies, middleware, and docs surfaces.
- Expose operational introspection through system routes.

## REST and JSON-RPC Surfaces

Concrete routing keeps REST and JSON-RPC projections tied to the same operation inventory:

| Surface | Concrete responsibility |
|---|---|
| REST | Aggregate route metadata, attach handlers, apply path/method mapping, shape request/response objects, and expose OpenAPI-compatible docs. |
| JSON-RPC | Resolve method names, validate JSON-RPC request/response models, dispatch through the same operation handlers, and expose OpenRPC-compatible docs. |
| Docs | Publish OpenAPI, OpenRPC, JSON Schema, Swagger, runtime operation views, and surface/lens outputs from the same concrete registration data. |
| Diagnostics | Expose `healthz`, `hookz`, `kernelz`, and `methodz` so users can inspect runtime health, hook order, kernel plans, and method inventory. |

Avoid adding one-off framework routes for model behavior when an operation spec can represent the behavior. Ops keep REST, JSON-RPC, docs, hooks, and diagnostics unified.

## Engine and Provider Behavior

The engine subpackage owns concrete engine resolution and plugin discovery. It can build and bind engines from specs, providers, mappings, or decorator metadata, then expose capability information for runtime and tests.

Resolution follows the framework's specificity rule:

```text
operation > table/model > router > app > defaults
```

Best practices:
- Declare engine intent through specs or decorators instead of constructing SQLAlchemy engines inside handlers.
- Keep engine plugins explicit and capability-aware.
- Test resolver behavior when adding a new engine package or new engine context shape.
- Preserve separation between engine resolution and transaction lifecycle; atoms/runtime own transaction phase progression.

## System and Operational Endpoints

Concrete apps can mount system endpoints:

- `/system/healthz` for basic process health.
- `/system/hookz` for model/operation/phase hook order.
- `/system/kernelz` for compiled kernel phase plans.
- `/system/methodz` for exposed method inventory.
- docs endpoints for OpenAPI, OpenRPC, JSON Schema, Swagger, and runtime operation surfaces.

These endpoints are operational tools. They should reflect registered framework state and compiled plans; do not hard-code documentation that can drift away from actual registrations.

## Security and Middleware

Security primitives include API key, HTTP Basic, HTTP Bearer, mutual TLS, OAuth2, and OpenID Connect helpers. Use them as dependencies or framework-level security specs so security behavior participates in lifecycle ordering and diagnostics. Middleware should be declared through concrete middleware helpers or specs rather than wrapping generated routes in ways the kernel cannot see.

## Extension Guidance

- Use concrete decorators and factories when building public conveniences for the facade.
- Keep compatibility imports in `tigrbl` thin; implement reusable behavior here or in lower packages.
- Do not bypass kernel/runtime plans when wiring REST or JSON-RPC handlers.
- Keep docs, diagnostics, and transport helpers generated from actual registration state.
- Treat `_concrete` classes as framework implementation surfaces; public application documentation should continue to prefer facade imports.

Authoring BCP for this boundary:
- Do use `tigrbl-concrete` to lower specs and base contracts into concrete app, router, table, operation, schema, request, response, engine, security, docs, diagnostics, and transport implementations.
- Do keep REST and JSON-RPC projections tied to the same operation inventory and handler resolution path.
- Do keep framework-internal ASGI, Starlette-compatible, SQLAlchemy, and engine mechanics behind concrete Tigrbl adapters.
- Do not teach application users to bypass the `tigrbl` facade and import `_concrete` classes for normal service code.
- Do not wire one-off handlers around kernel/runtime plans, diagnostics, generated docs, or operation specs.
- Avoid hard-coded documentation and diagnostics that can drift away from actual registrations.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-concrete
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-concrete"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_concrete")
print(module.__name__)
```

### Inspect available modules

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_concrete")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-concrete
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-concrete` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
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
- Repository: [pkgs/core/tigrbl_concrete](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_concrete).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-concrete`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
