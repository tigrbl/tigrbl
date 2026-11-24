# tigrbl-concrete

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-concrete</strong></p>
<p align="center">Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-concrete/"><img alt="pypi: tigrbl-concrete" src="https://img.shields.io/pypi/v/tigrbl-concrete?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml"><img alt="Layer: 70_concrete" src="https://img.shields.io/static/v1?label=Layer&amp;message=70_concrete&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-concrete/"><img alt="Monthly PyPI downloads: tigrbl-concrete" src="https://img.shields.io/pypi/dm/tigrbl-concrete?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/README.md"><img alt="README hits: tigrbl-concrete" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/70_concrete/tigrbl_concrete/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-concrete`: Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-concrete` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `Alias`: Concrete alias type.
- `App`: declared in tigrbl_concrete/_concrete/_app.py
- `BackgroundTask`: Run a callable after response handling, matching Starlette semantics.
- `Binding`: Concrete named binding declaration.
- `BindingRegistry`: Concrete named binding registry.
- `Body`: Lightweight wrapper for response/request payload bytes.
- `Column`: Concrete SQLAlchemy column implementing a :class:`ColumnSpec`.
- `CORSMiddleware`: declared in tigrbl_concrete/_concrete/_cors_middleware.py

### Non-Goals

`tigrbl-concrete` owns concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml) declares runtime dependencies including `orjson`, `pydantic`, `sqlalchemy`, `tigrbl-atoms`, `tigrbl-base`, `tigrbl-core`, `tigrbl-ops-olap`, `tigrbl-ops-oltp`, `tigrbl-ops-realtime`, `tigrbl-ops-webtransport`, `tigrbl-runtime`, `tigrbl-typing`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-concrete
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-concrete
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-concrete
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_concrete")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-concrete` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_concrete")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-concrete
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-concrete"))
PY
```

**Import the package boundary**


**Inspect available modules**

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_concrete")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-concrete
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete/__init__.py) references configuration keys `CONTENT_LENGTH`, `PATH_INFO`, `PGDATABASE`, `PGHOST`, `PGPASSWORD`, `PGPORT`, `PGUSER`, `QUERY_STRING`, `REQUEST_METHOD`, `SCRIPT_NAME`, `TABLES`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `tigrbl-concrete` source raises `AttributeError`, `HTTPException`, `InvalidHookPhaseError`, `KeyError`, `LookupError`, `NotImplementedError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-concrete` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Any`, `annotations`, `import_module`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

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

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-concrete`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_concrete`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `orjson`, `pydantic>=2.0`, `sqlalchemy`, `uvicorn`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `concrete` → `tigrbl_concrete.engine.plugins:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-concrete` are `orjson`, `pydantic`, `sqlalchemy`, `tigrbl-atoms`, `tigrbl-base`, `tigrbl-core`, `tigrbl-ops-olap`, `tigrbl-ops-oltp`, `tigrbl-ops-realtime`, `tigrbl-ops-webtransport`, `tigrbl-runtime`, `tigrbl-typing`, `uvicorn`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-runtime-identity-storage`, `tba-workspace`, `tigrbl`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-concrete`, use the source-declared public interfaces (`Any`, `annotations`, `import_module`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-concrete` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-concrete`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete/__init__.py). The `tigrbl-concrete` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-concrete` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-concrete` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_appspec_engine_inventory_lowering.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tests/test_appspec_engine_inventory_lowering.py)
- [tests/test_appspec_webtransport_lowering.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tests/test_appspec_webtransport_lowering.py)
- [tests/test_asgi3_callable.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tests/test_asgi3_callable.py)
- [tests/test_async_generator_dependencies.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tests/test_async_generator_dependencies.py)
- [tests/test_column_spec_aliases.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tests/test_column_spec_aliases.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-concrete` provides concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-concrete`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/tigrbl_concrete/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-concrete` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [Next steps](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/NEXT_STEPS.md)
- [Documentation pointers](https://github.com/tigrbl/tigrbl/blob/master/docs/governance/DOC_POINTERS.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

### Related Packages

- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/70_concrete/tigrbl_concrete)
- [pypi: tigrbl-concrete](https://pypi.org/project/tigrbl-concrete/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/70_concrete/tigrbl_concrete](https://github.com/tigrbl/tigrbl/tree/master/pkgs/70_concrete/tigrbl_concrete).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-concrete`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/70_concrete/tigrbl_concrete` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-concrete?**

Concrete Tigrbl implementations for reusable framework behavior, sessions, routes, responses, and base abstraction adapters.

**When should I install tigrbl-concrete?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-concrete for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-concrete fit?**

`tigrbl-concrete` lives at `pkgs/70_concrete/tigrbl_concrete` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-concrete work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-concrete
```

```bash
pip install tigrbl-concrete
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/) |
| Repository path | [`pkgs/70_concrete/tigrbl_concrete`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/70_concrete/tigrbl_concrete) |
| Python import root | `tigrbl_concrete` |
| Console scripts | none declared |
| Entry points | `tigrbl.engine_plugins` |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Concrete Implementation Semantics**

`tigrbl-concrete` is where abstract specs and base contracts become usable Python framework objects. It is intentionally below the `tigrbl` facade and above the atom/kernel/runtime internals. Application developers normally import through `tigrbl`; extension authors import this package when they need concrete classes, decorators, engine resolution, docs mounting, or diagnostics without taking the facade dependency.

The package performs four broad jobs:

- Lower core specs and base contracts into concrete app/router/table/operation objects.
- Register REST and JSON-RPC projections for model operations.
- Resolve engines, handlers, schemas, responses, security dependencies, middleware, and docs surfaces.
- Expose operational introspection through system routes.

**REST and JSON-RPC Surfaces**

Concrete routing keeps REST and JSON-RPC projections tied to the same operation inventory:

| Surface | Concrete responsibility |
|---|---|
| REST | Aggregate route metadata, attach handlers, apply path/method mapping, shape request/response objects, and expose OpenAPI-compatible docs. |
| JSON-RPC | Resolve method names, validate JSON-RPC request/response models, dispatch through the same operation handlers, and expose OpenRPC-compatible docs. |
| Docs | Publish OpenAPI, OpenRPC, JSON Schema, Swagger, runtime operation views, and surface/lens outputs from the same concrete registration data. |
| Diagnostics | Expose `healthz`, `hookz`, `kernelz`, and `methodz` so users can inspect runtime health, hook order, kernel plans, and method inventory. |

Avoid adding one-off framework routes for model behavior when an operation spec can represent the behavior. Ops keep REST, JSON-RPC, docs, hooks, and diagnostics unified.

**Engine and Provider Behavior**

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

**System and Operational Endpoints**

Concrete apps can mount system endpoints:

- `/system/healthz` for basic process health.
- `/system/hookz` for model/operation/phase hook order.
- `/system/kernelz` for compiled kernel phase plans.
- `/system/methodz` for exposed method inventory.
- docs endpoints for OpenAPI, OpenRPC, JSON Schema, Swagger, and runtime operation surfaces.

These endpoints are operational tools. They should reflect registered framework state and compiled plans; do not hard-code documentation that can drift away from actual registrations.

**Security and Middleware**

Security primitives include API key, HTTP Basic, HTTP Bearer, mutual TLS, OAuth2, and OpenID Connect helpers. Use them as dependencies or framework-level security specs so security behavior participates in lifecycle ordering and diagnostics. Middleware should be declared through concrete middleware helpers or specs rather than wrapping generated routes in ways the kernel cannot see.

**Extension Guidance**

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

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-concrete` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-concrete` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/70_concrete/tigrbl_concrete/NOTICE) for attribution.
<!-- readme-standards:end notices -->
