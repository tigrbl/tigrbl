# tigrbl-core

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-core</strong></p>
<p align="center">Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-core/"><img alt="pypi: tigrbl-core" src="https://img.shields.io/pypi/v/tigrbl-core?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml"><img alt="Source version: 0.4.6.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml"><img alt="Layer: 10_core" src="https://img.shields.io/static/v1?label=Layer&amp;message=10_core&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-core/"><img alt="Monthly PyPI downloads: tigrbl-core" src="https://img.shields.io/pypi/dm/tigrbl-core?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/README.md"><img alt="README hits: tigrbl-core" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/10_core/tigrbl_core/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-core`: Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-core` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-core` owns core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml) declares runtime dependencies including `tigrbl-spec`, `tigrbl-typing`, `pydantic`, `pyyaml`, `tomli-w`, `tomli`. Use the source-checkout workflow for this workspace or test harness.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-core
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-core
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-core
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_core._spec")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-core` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_core._spec")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-core
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-core"))
PY
```

**Import the package boundary**


**Inspect available modules**

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_core._spec")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-core
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl-core` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-core` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-core` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-core` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_core`: _spec/, canonical_json, config/, core/, op/, schema/

Package catalog:
- `tigrbl_core/_spec/`: typed, serializable specifications for aliases, apps, bindings, columns, data types, docs, engines, fields, hooks, IO, middleware, operations, paths, requests, responses, routers, schemas, sessions, storage, tables, and table registries.
- `tigrbl_core/config/`: constants, defaults, resolver logic, and engine traversal helpers used when app, router, table, column, op, and request layers are merged.
- `tigrbl_core/op/`: canonical operation names, operation collection, and operation typing helpers.
- `tigrbl_core/schema/`: dynamic schema construction, schema cache helpers, extras handling, list-parameter support, schema JSON helpers, and `get_schema` access.
- `tigrbl_core/canonical_json.py`: deterministic JSON output used by docs, registry-like payloads, tests, and conformance artifacts.

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-core`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_core`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `pydantic>=2.10,<3`, `pyyaml`, `tomli-w`, `tomli>=2.0.1; python_version < '3.11'`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-core` are `tigrbl-spec`, `tigrbl-typing`, `pydantic`, `pyyaml`, `tomli-w`, `tomli`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-storage-core`, `tba-runtime-identity-storage`, `tba-server-identity`, `tba-workspace`, `tigrbl-base`, `tigrbl-atoms`, `tigrbl-kernel`, `tigrbl-runtime`, `tigrbl-ops-oltp`, `tigrbl-concrete`, `tigrbl`, `tigrbl-equivalence-contracts`, `tigrbl-transport-surface-matrix-demo`, `tigrbl-websocket-realtime-ops-demo`, `tigrbl-mcp`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-core`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-core` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-core`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml). The `tigrbl-core` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-core` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-core` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_adapter_registry_contract.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/tests/test_adapter_registry_contract.py)
- [tests/test_alias_spec.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/tests/test_alias_spec.py)
- [tests/test_app_spec.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/tests/test_app_spec.py)
- [tests/test_binding_spec.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/tests/test_binding_spec.py)
- [tests/test_canonical_appspec_transport_contract.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/tests/test_canonical_appspec_transport_contract.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-core` provides core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-core`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-core` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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

- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/10_core/tigrbl_core)
- [pypi: tigrbl-core](https://pypi.org/project/tigrbl-core/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/10_core/tigrbl_core](https://github.com/tigrbl/tigrbl/tree/master/pkgs/10_core/tigrbl_core).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-core`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/10_core/tigrbl_core` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-core?**

Core Tigrbl framework specifications, decorators, schemas, hooks, operations, and primitives for schema-first APIs.

**When should I install tigrbl-core?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-core for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-core fit?**

`tigrbl-core` lives at `pkgs/10_core/tigrbl_core` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-core work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-core
```

```bash
pip install tigrbl-core
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-core`](https://pypi.org/project/tigrbl-core/) |
| Repository path | [`pkgs/10_core/tigrbl_core`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/10_core/tigrbl_core) |
| Python import root | `tigrbl_core` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Specification Model**

The core package is the contract layer. It defines the vocabulary consumed by base abstractions, concrete adapters, atoms, kernel planning, runtime routing, docs generation, and the public facade. Most application code should not construct these specs manually; application code should normally use facade decorators and shortcuts. Extension packages use the specs when they need deterministic, testable configuration objects.

| Spec family | What it describes |
|---|---|
| `AppSpec`, `RouterSpec`, `TableSpec` | Container-level framework configuration and inheritance points. |
| `ColumnSpec`, `FieldSpec`, data type specs | Field semantics, validation, storage, schema projection, and data-type lowering. |
| `OpSpec` and op utilities | Operation name, alias, arity, binding, handler, schema, hook, response, and runtime intent. |
| `HookSpec` and hook types | Hook targets, phases, predicates, ordering, and callable registration shape. |
| `SchemaSpec`, `RequestSpec`, `ResponseSpec`, `IoSpec` | Input/output envelope behavior, request extraction, response shaping, and Pydantic model generation. |
| `BindingSpec` | REST, JSON-RPC, stream, SSE, WebSocket, WSS, and WebTransport binding metadata. |
| `EngineSpec`, `SessionSpec`, `StorageSpec` | Engine/provider/session/storage configuration without importing concrete engine implementations. |
| `DocsSpec`, `PathSpec`, `MiddlewareSpec` | Documentation projection, route paths, and middleware configuration. |

**Operation Semantics**

`tigrbl_core.op.canonical.DEFAULT_CANON_VERBS` is the default CRUD set:

```text
create, read, update, replace, delete, list, clear
```

Tables can change canonical wiring through mode/include/exclude attributes or a `should_wire_canonical(op)` helper. Core only decides whether an operation is part of the desired specification. Concrete packages and operation packs supply the actual handlers and routing behavior.

Use this package when you need to inspect or build operation specs before runtime compilation. Use `tigrbl` when you simply want a working app surface.

**Binding and Transport Semantics**

`BindingSpec` keeps four concerns distinct:

- protocol or binding kind, such as HTTP REST, HTTP JSON-RPC, HTTP stream, SSE, WebSocket, WSS, or WebTransport;
- exchange shape, such as request/response, server stream, bidirectional stream, client stream, server stream, session, or datagram;
- framing, such as JSON, JSON-RPC, SSE, WebSocket text, stream framing, or WebTransport lane-local framing;
- runtime lane metadata, especially for WebTransport session, stream, and datagram behavior.

This separation is deliberate. Extension authors should not collapse protocol support into a single string or infer framing from the transport name. Invalid combinations should remain explicit validation failures so runtime behavior is fail-closed.

**Configuration Precedence**

Core resolvers use this precedence pattern:

```text
request override > operation spec > column spec > table spec > router spec > app spec > defaults
```

The most specific layer wins. Keep default policy broad, then narrow behavior by table, column, and operation. Avoid hidden mutation of spec objects after a runtime plan has been compiled; build a fresh spec or invalidate the relevant cache when behavior truly changes.

**Schema Construction**

Schema helpers build operation-specific request and response models from table metadata, column specs, request/response extras, list-parameter rules, and op-level configuration. `get_schema(...)` is the stable way to retrieve the generated model for a table operation and direction. Prefer it over hand-writing duplicate Pydantic envelopes when data belongs to a Tigrbl operation.

Best practices for schema work:
- Keep storage fields, wire fields, and virtual extras separate.
- Put reusable schema behavior in table or column specs; reserve op specs for operation-specific differences.
- Use canonical JSON helpers when writing deterministic docs or evidence artifacts.
- Treat generated schemas as projections of the specs, not as the source of truth.

**Extension Guidance**

- Depend on `tigrbl-core` when you need spec classes, op collection, schema generation, or config resolution without concrete app/router/runtime imports.
- Keep specs serializable and deterministic. Do not attach live database sessions, request objects, or transport handles to core specs.
- Validate protocol and binding assumptions in core or kernel-facing tests before adding runtime behavior.
- Keep application-facing convenience APIs in `tigrbl` or `tigrbl-concrete`; keep cross-package contracts here.

Authoring BCP for this boundary:
- Do treat `ColumnSpec`, `FieldSpec`, `OpSpec`, `HookSpec`, `SchemaSpec`, `BindingSpec`, `EngineSpec`, `SessionSpec`, and related specs as the contract vocabulary that other Tigrbl packages consume.
- Do keep specs independent of FastAPI, Starlette, SQLAlchemy sessions, live request objects, and transport handles.
- Do not move application route authoring, direct database calls, concrete engine creation, or runtime dispatch side effects into `tigrbl-core`.
- Avoid duplicating spec fields in helper classes or generated schemas. Specs should remain the source that schema, docs, kernel, runtime, base, concrete, and facade layers project from.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-core` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-core` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/10_core/tigrbl_core/NOTICE) for attribution.
<!-- readme-standards:end notices -->
