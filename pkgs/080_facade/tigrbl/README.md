# tigrbl

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl</strong></p>
<p align="center">Schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, runtime plans, hooks, diagnostics, and engine plugins.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl/"><img alt="pypi: tigrbl" src="https://img.shields.io/pypi/v/tigrbl?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml"><img alt="Source version: 0.4.6.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml"><img alt="Layer: 080_facade" src="https://img.shields.io/static/v1?label=Layer&amp;message=080_facade&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl/"><img alt="Monthly PyPI downloads: tigrbl" src="https://img.shields.io/pypi/dm/tigrbl?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/README.md"><img alt="README hits: tigrbl" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/080_facade/tigrbl/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl`: Schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, runtime plans, hooks, diagnostics, and engine plugins.

### Why This Package

Use it when you want the public Tigrbl authoring surface in one install target instead of composing split packages by hand.

### When to Use

Choose `tigrbl` when you want the full public facade: app composition, schema-first routing, REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, docs generation, engine integration, and CLI workflow. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) only when you are building framework extensions or testing a specific internal boundary.

### Features

- `CLIError`: User-facing CLI validation error.
- `ServeConfig`: declared in tigrbl/cli.py

### Non-Goals

`tigrbl` owns schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, runtime plans, hooks, diagnostics, and engine plugins. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml) declares runtime dependencies including `tigrbl-core`, `tigrbl-base`, `tigrbl-concrete`, `tigrbl-canon`, `tigrbl-orm`, `tigrbl-runtime`, `tigrbl-atoms`, `tigrbl-kernel`, `tigrbl-ops-oltp`, `pydantic`, `sqlalchemy`, `aiosqlite`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/docs/readme/quick_start.py).

```python
from tigrbl import TigrblApp, TigrblRouter

app = TigrblApp()
router = TigrblRouter()
app.include_router(router)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/docs/readme/usage.py).

```python
from tigrbl import TigrblApp, TigrblRouter

app = TigrblApp()
router = TigrblRouter()
app.include_router(router)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl"))
PY
```

**Create a small Tigrbl app shell**


**Use author-facing decorators**

```python
from tigrbl import get, post

@get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@post("/items")
def create_item(payload: dict) -> dict:
    return payload
```

**Run the console entry point**

```bash
tigrbl --help
python -m tigrbl --help
```

### Configuration

Declare protected actions with `OperationSecurity` and register the decision
with `app.set_auth(authorize=authorize)` or the router equivalent.
The callback receives `request, model, alias, payload, user`. For a protected
operation it can also declare a keyword-only `ctx` and read the compiled
declaration from `ctx["operation_security"]`. It must return `True` in
`SECURITY` before Tigrbl runs `DEPENDENCIES` and application `PRE_TX_BEGIN` hooks.

Configure `tigrbl` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tigrbl/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

- Do: Handle validation and authorization failures at their operation or CLI boundary, preserving typed errors for the transport binding.
- Why: Callers depend on predictable status codes and error envelopes to distinguish invalid input, denied access, and execution failures.
- Avoid: Returning a success response after a failed operation or exposing credentials and internal tracebacks in public error messages.

The inspected `tigrbl` source raises `AttributeError`, `CLIError`, `KeyError`, `SystemExit`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Use `tigrbl` facade imports in application code; import split packages directly only for framework extension work.
- Model domain actions as operations, not ad-hoc routes, so REST, JSON-RPC, schemas, hooks, OpenAPI, OpenRPC, and diagnostics stay in sync.
- Use `get_schema(...)` or schema helpers for request/response envelopes instead of hand-rolled Pydantic classes when the payload belongs to a Tigrbl operation.
- Keep `Table` first in model inheritance when using ORM table classes so table inspection and MRO-sensitive behavior stay deterministic.
- Bind engines declaratively at app, router, table, or operation scope; do not create engines inside request handlers.
- Let the lifecycle own transaction boundaries; avoid direct `flush()`, `commit()`, and SQLAlchemy session mutation from user hooks.
- Put authentication/authorization in security dependencies or `PRE_HANDLER` hooks, not in transport-specific route wrappers.
- Use `/system/hookz`, `/system/kernelz`, docs endpoints, OpenAPI, and OpenRPC outputs as operational inspection surfaces during debugging.
- Treat unsupported transport/framing combinations as unsupported, not broken. Preserve fail-closed behavior unless the underlying binding and runtime packages are intentionally extended.

---

## Package Boundary

### What It Owns

`tigrbl` owns the `public facade package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl`: __main__, canonical_json, cli, config/, ddl/, decorators/, engine/, factories/, hook/, middlewares/, op/, orm/

Facade orientation:
- Authoring API: app/router factories, table helpers, column helpers, schema helpers, operation decorators, hook decorators, response decorators, and engine decorators.
- Compatibility imports: facade modules such as `tigrbl.op`, `tigrbl.config`, `tigrbl.schema`, `tigrbl.ddl`, `tigrbl.security`, and `tigrbl.system` forward into the split packages that now own the implementation.
- Runtime projection: model operations are compiled into REST bindings, JSON-RPC methods, HTTP streams, SSE responses, WebSocket channels, WebTransport-aware runtime units, OpenAPI, OpenRPC, diagnostics, schemas, and engine-backed handlers.
- Operational boundary: this package is the application-facing install target; lower-level packages own specs, atoms, kernel planning, runtime execution, base abstractions, concrete adapters, ORM helpers, and engine plugins.

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl`.
- Public symbols: `APIKey`, `Alias`, `App`, `AppBase`, `AppSpec`, `Arity`, `BINDING_PROFILE_EXCHANGE_SUPPORT`, `BackgroundTask`, `Binding`, `BindingRegistry`, `BindingRegistrySpec`, `BindingSpec`.
- Workspace dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/), [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/), [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/), [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/).
- External runtime dependencies: `pydantic>=2.0.0`, `sqlalchemy>=2.0`, `aiosqlite>=0.19.0`, `httpx>=0.27.0`, `greenlet>=3.2.3`, `uvicorn`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `tigrbl` → `tigrbl.cli:console_main`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl` are `tigrbl-core`, `tigrbl-base`, `tigrbl-concrete`, `tigrbl-canon`, `tigrbl-orm`, `tigrbl-runtime`, `tigrbl-atoms`, `tigrbl-kernel`, `tigrbl-ops-oltp`, `pydantic`, `sqlalchemy`, `aiosqlite`, `httpx`, `greenlet`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tigrbl/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-storage-access-governance`, `tba-storage-attestation`, `tba-storage-audit`, `tba-storage-authentication`, `tba-storage-authority-graph`, `tba-storage-authorization-policy`, `tba-storage-certificate`, `tba-storage-claims`, `tba-storage-consent`, `tba-storage-core`, `tba-storage-delegation`, `tba-storage-did`, `tba-storage-digital-credential`, `tba-storage-federation`, `tba-storage-gnap`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl`, use the source-declared public interfaces (`APIKey`, `Alias`, `App`, `AppBase`, `AppSpec`, `Arity`, `BINDING_PROFILE_EXCHANGE_SUPPORT`, `BackgroundTask`, `Binding`, `BindingRegistry`, `BindingRegistrySpec`, `BindingSpec`, `BulkCrudTable`, `CORSMiddleware`, `Column`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tigrbl/__init__.py). The `tigrbl` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_facade_exports.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tests/test_facade_exports.py)
- [tests/test_mysql_factory_aliases.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tests/test_mysql_factory_aliases.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/210_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tigrbl/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl` provides schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, runtime plans, hooks, diagnostics, and engine plugins; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/tigrbl/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

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

### Related Packages

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl)
- [pypi: tigrbl](https://pypi.org/project/tigrbl/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/080_facade/tigrbl](https://github.com/tigrbl/tigrbl/tree/master/pkgs/080_facade/tigrbl).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/080_facade/tigrbl` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl?**

Schema-first ASGI framework for REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, OpenAPI, OpenRPC, typed validation, hooks, diagnostics, and engine plugins.

**When should I install tigrbl?**

Install it for application projects, examples, service skeletons, and teams that want REST, JSON-RPC, streaming, SSE, WebSocket, docs, schemas, engines, and CLI support from one facade.

**Who is tigrbl for?**

Application developers, platform teams, and service owners building schema-first Python APIs.

**Where does tigrbl fit?**

`tigrbl` lives at `pkgs/080_facade/tigrbl` and serves schema-first service authoring, REST, JSON-RPC, streaming, SSE, WebSocket, WebTransport-aware runtime planning, docs, engines, and CLI workflows.

**How does tigrbl work?**

It re-exports stable author-facing classes and decorators while delegating resident behavior to core, base, runtime, kernel, atoms, ORM, and operation packages.

**Install**

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

The base install uses the Python dispatcher. Install `tigrbl[numba]` to use Numba-compiled route dispatch with the `numba_packed` executor.

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl`](https://pypi.org/project/tigrbl/) |
| Repository path | [`pkgs/080_facade/tigrbl`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/080_facade/tigrbl) |
| Python import root | `tigrbl` |
| Console scripts | `tigrbl` |
| Entry points | none declared |
| Optional extras | `numba`, `postgres`, `servers`, `templates`, `tests` |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Framework Catalog**

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
| Operation packs | `tigrbl-ops-oltp`, `tigrbl-ops-olap`, `tigrbl-ops-realtime`, `tigrbl-ops-webtransport` | Canonical operation definitions for CRUD, analytics, realtime/streaming, and WebTransport control-plane workloads. |
| ORM | `tigrbl-orm` | SQLAlchemy-facing table and mixin helpers used by application models. |
| Engines | `tigrbl-engine-*` | Persistence, cache, queue, rate, bloom, dedupe, dataframe, warehouse, and database engine integrations. |

Use the facade for application code unless you are maintaining a framework layer, testing a boundary in isolation, or writing a package that intentionally plugs into one of the lower layers.

<!-- tigrbl:authoring-bcp:begin -->
**Convenient Authoring Path and Best Current Practice (BCP)**

Tigrbl is most convenient when application code describes behavior once and lets the framework project that behavior into routes, RPC methods, schemas, docs, lifecycle hooks, diagnostics, tests, and transport-aware runtime plans. The best current practice is to use tables, default canonical operations, operation specs, custom handlers, and lifecycle hooks together instead of spreading one behavior across lower-level framework surfaces. The detailed policy is in [`docs/developer/AUTHORING_BCP.md`](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/AUTHORING_BCP.md).

For readers translating from Starlette, FastAPI, Flask, ASGI 3, WebSocket,
WebTransport, SQLAlchemy, or database-engine concepts, use
[`docs/developer/EQUIVALENCE_INDEX.md`](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/EQUIVALENCE_INDEX.md).
Those guides explain nearby concepts without making lower-layer frameworks the
Tigrbl application authoring contract.

**Keep the facade as the application contract**

- Avoid: Treating ASGI, FastAPI, Flask, Starlette, SQLAlchemy ORM materialization, or direct database/session calls as the user-facing application contract.
- Do: Build application services with `TigrblApp`, `TigrblRouter`, facade decorators, table helpers, column helpers, operation specs, hook specs, binding specs, engine specs, and generated schemas.
- Why: Tigrbl-owned authoring surfaces are the entry points that runtime planning, docs, diagnostics, schemas, and tests understand.

**Start with tables and default canonical operations**

- Avoid: Hand-writing endpoint-specific behavior before checking whether table-backed default operations already express it.
- Do: Model resources with Tigrbl tables and use default canonical operations such as `create`, `read`, `update`, `replace`, `delete`, `list`, and `clear` where they fit.
- Why: Tables plus canonical operations give Tigrbl a durable resource model that can be projected consistently across REST, JSON-RPC, schemas, docs, hooks, diagnostics, and tests.

**Use operations and custom handlers for domain actions**

- Avoid: Splitting one domain action across separate REST handlers, JSON-RPC handlers, stream handlers, docs snippets, and protocol-specific wrappers.
- Do: Model domain actions as Tigrbl operations with operation specs and custom handlers when the default canonical operations are not enough.
- Why: Operations are the unit Tigrbl can bind, document, inspect, test, and project across protocol surfaces.

**Use lifecycle hooks around operations**

- Avoid: Embedding lifecycle policy directly inside transport-specific handlers or lower-level framework middleware.
- Do: Use lifecycle hooks around operations for validation, authorization, enrichment, auditing, response shaping, rollback handling, and post-response work.
- Why: Hooks make behavior visible before and after the operation, while preserving lifecycle ordering across REST, JSON-RPC, streams, SSE, WebSocket, and WebTransport-aware runtime plans.

**Support persistence and non-persistence operations**

- Avoid: Assuming every operation or custom handler must be database-backed.
- Do: Use operations and custom handlers for persistence workflows and for non-persistence workflows such as computed responses, orchestration, control-plane commands, stream/session commands, or external-service actions.
- Why: The operation model gives both persistence and non-persistence behavior the same docs, hooks, diagnostics, protocol projection, and runtime planning path.

**Put field behavior in Tigrbl specs**

- Avoid: Duplicating field behavior across SQLAlchemy declarations, Pydantic models, route handlers, and docs.
- Do: Describe field behavior through Tigrbl tables, `FieldSpec`, `ColumnSpec`, `StorageSpec`, and `IOSpec`.
- Why: These specs keep field semantics aligned for storage lowering, validation, schemas, docs, hooks, diagnostics, and runtime planning.

**Use generated schemas for operation payloads**

- Avoid: Hand-written Pydantic envelopes for payloads that belong to a Tigrbl operation.
- Do: Use `get_schema(...)` or other Tigrbl schema helpers for operation request and response payloads.
- Why: Generated schemas keep payloads aligned with operation specs, docs, validation, and protocol projections.

**Keep engines and transactions declarative**

- Avoid: Creating ad-hoc SQLAlchemy engines, sessions, sessionmakers, commits, or flushes inside application handlers.
- Do: Bind engines declaratively at app, router, table, or operation scope, and let kernel/runtime phases own dispatch and transaction progression.
- Why: Declarative binding lets the runtime own session selection, transaction scope, rollback behavior, pooling, diagnostics, backend adapters, and post-response work.

**Keep examples in Tigrbl style**

- Avoid: README examples that present lower-level framework internals as normal application style.
- Do: Use Tigrbl facade imports and Tigrbl-owned authoring surfaces in application examples unless the example is explicitly marked as a lower-layer test, benchmark, migration, engine adapter, or framework-internal compatibility example.
- Why: Examples should show the framework path that keeps operations, schemas, docs, hooks, diagnostics, and runtime planning aligned.

**Keep workspace docs in their right lanes**

- Avoid: Using the root README as the only documentation for a distributable package.
- Do: Use package-local README files to explain package boundaries, install targets, import roots, dependency surfaces, usage examples, and links to governed docs.
- Why: The root README orients the workspace, while package READMEs serve PyPI users who arrive at one install target.

**Do not wire endpoints around the operation plan**

- Do not: Bypass operation specs, handlers, kernel plans, runtime atoms, or lifecycle phases with one-off route wrappers for REST, JSON-RPC, HTTP stream, SSE, WebSocket, or WebTransport behavior.
- Do: Define the operation once, bind it through Tigrbl specs, and let kernel/runtime planning own protocol dispatch.
- Why: This preserves legality checks, lifecycle phases, transaction ownership, protocol framing policy, and fail-closed unsupported-combination handling.

**Do not make lower-level frameworks the application surface**

- Do not: Author Tigrbl application endpoints with FastAPI `FastAPI`, `APIRouter`, dependency wiring, route decorators, middleware registration, docs generation, or application lifecycle wiring.
- Do: Use Tigrbl app/router factories, decorators, tables, default canonical operations, operation specs, custom handlers, lifecycle hooks, schema helpers, and engine decorators.
- Why: FastAPI is a substrate here; Tigrbl is the application contract that keeps operations, bindings, hooks, schemas, docs, diagnostics, and tests together.

**Do not route around the runtime substrate boundary**

- Do not: Author application endpoints directly with Starlette route, request, response, middleware, background-task, or application lifecycle classes.
- Do: Express application behavior through Tigrbl operations, bindings, lifecycle hooks, and runtime-managed execution.
- Why: Starlette is a lower-level runtime substrate here, not the application-facing authoring surface.

**Do not fragment behavior into Flask route objects**

- Do not: Author application endpoints with Flask `Flask`, `Blueprint`, route decorators, request/response globals, `MethodView`, extension registration, or application lifecycle hooks.
- Do: Keep resources in tables, use default canonical operations where they fit, and use operation specs plus custom handlers for domain actions.
- Why: Flask route objects cannot preserve Tigrbl's shared operation inventory, schema generation, lifecycle phases, hook ordering, or transport plan.

**Do not use raw ORM declarations as the primary application model**

- Do not: Use raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the primary application authoring surface when Tigrbl specs can represent the field behavior.
- Do: Describe field behavior through Tigrbl tables, `FieldSpec`, `ColumnSpec`, `StorageSpec`, and `IOSpec`.
- Why: Raw ORM declarations are only one lowering target and cannot carry the full storage, IO, validation, docs, hook, and runtime contract.

**Do not manage database state inside handlers**

- Do not: Call direct database/session methods such as `flush()` or `commit()` from application hooks or handlers.
- Do: Let lifecycle phases such as `START_TX`, `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, and `TX_COMMIT` own transaction progression.
- Why: Direct calls bypass lifecycle guards and can commit partial state before hooks, errors, rollback handlers, or response shaping have run.

**Do not blur package boundaries**

- Do not: Widen a package boundary by adding dependencies, imports, examples, or docs that belong in another split package.
- Do: Keep facade guidance in `tigrbl`, framework internals in the lower-level packages that own them, and package-specific usage in package-local READMEs.
- Why: Clear package boundaries make the split distribution convenient instead of surprising, especially for users installing only one package.

**Keep release and certification claims governed**

- Avoid: Duplicating release, certification, target-state, or conformance claims outside governed evidence records.
- Do: Use `.ssot/`, conformance docs, release evidence, and certification reports for governed feature, claim, release, evidence, and target-state questions.
- Why: Release status and proof chains need one source of truth so package docs do not drift from CI and certification evidence.

<!-- tigrbl:authoring-bcp:end -->

**Default CRUD and Operation Semantics**

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

**Bulk Operation Shape Reference**

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

**REST, JSON-RPC, and Transport Projection**

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

**Request Lifecycle and Hook Phases**

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

**Step Types and Kernel Labels**

Execution plans are composed from labeled steps:

| Step type | Owner | Purpose |
|---|---|---|
| `secdep` | Application or security package | Authentication and authorization dependencies that run before ordinary dependencies. |
| `dep` | Application or extension package | General dependency resolution and request context hydration. |
| `hook:sys` | Tigrbl | Built-in system hooks for runtime behavior, transaction handling, schema work, and transport work. |
| `hook:wire` | Application or extension package | User hooks registered through decorators or specs. |
| `atom:<domain>:<subject>` | Tigrbl atoms/kernel | Small runtime units such as ingress parsing, dispatch, validation, handler invocation, response shaping, or transport emission. |

Kernel labels make execution order reviewable, for example `PRE_HANDLER:hook:wire:myapp.audit@PRE_HANDLER` or `EGRESS_SHAPE:atom:wire:dump`. Treat labels as diagnostics, not as a stable replacement for the public decorator/spec APIs.

**Engine and Session Semantics**

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

**Configuration and Schema Precedence**

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

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/080_facade/tigrbl/NOTICE) for attribution.
<!-- readme-standards:end notices -->
