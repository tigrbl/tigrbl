# tigrbl-base

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-base</strong></p>
<p align="center">Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-base/"><img alt="pypi: tigrbl-base" src="https://img.shields.io/pypi/v/tigrbl-base?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml"><img alt="Layer: 020_base" src="https://img.shields.io/static/v1?label=Layer&amp;message=020_base&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-base/"><img alt="Monthly PyPI downloads: tigrbl-base" src="https://img.shields.io/pypi/dm/tigrbl-base?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/README.md"><img alt="README hits: tigrbl-base" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/020_base/tigrbl_base/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-base`: Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-base` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-base` owns base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml) declares runtime dependencies including `tigrbl-core`, `tigrbl-atoms`, `sqlalchemy`, `pydantic`. Use the source-checkout workflow for this workspace or test harness.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-base
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-base
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-base
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_base._base")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-base` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_base._base")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-base
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-base"))
PY
```

**Import the package boundary**


**Inspect available modules**

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_base._base")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-base
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl-base` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-base` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-base` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-base` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_base`: _base/, column/

Package catalog:
- `_base/_app_base.py`, `_router_base.py`, and `_table_base.py`: abstract app, router, and table behavior used by concrete framework classes.
- `_base/_op_base.py`, `_binding_base.py`, `_rest_map.py`, and `_rpc_map.py`: operation, binding, REST mapping, and JSON-RPC mapping contracts.
- `_base/_schema_base.py`, `_request_base.py`, `_response_base.py`, `_headers_base.py`, and `_middleware_base.py`: request/response/schema/header/middleware abstractions.
- `_base/_engine_base.py`, `_engine_provider_base.py`, `_session_abc.py`, `_session_base.py`, and `_storage.py`: engine, provider, session, and storage interfaces.
- `_base/_column_base.py`, `_table_registry_base.py`, `_alias_base.py`, `_hook_base.py`, `_security_base.py`, and `_datatype_lowering.py`: table metadata, aliasing, hook/security contracts, and data-type lowering hooks.
- `_base/_assembly.py` and `_mapping_access.py`: assembly and mapping helpers for concrete implementations.
- `column/infer`: column inference planning, JSON hint handling, type interpretation, and utility helpers.

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-base`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_base`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/).
- External runtime dependencies: `sqlalchemy>=2.0`, `pydantic>=2.0`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-base` are `tigrbl-core`, `tigrbl-atoms`, `sqlalchemy`, `pydantic`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-runtime`, `tigrbl-ops-oltp`, `tigrbl-concrete`, `tigrbl`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-base`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-base` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-base`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml). The `tigrbl-base` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-base` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-base` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_alias_base.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/tests/test_alias_base.py)
- [tests/test_app_base.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/tests/test_app_base.py)
- [tests/test_app_bind_spec.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/tests/test_app_bind_spec.py)
- [tests/test_base_export_surface_contracts.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/tests/test_base_export_surface_contracts.py)
- [tests/test_binding_base.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/tests/test_binding_base.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/210_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-base` provides base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-base`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-base` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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

- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/020_base/tigrbl_base)
- [pypi: tigrbl-base](https://pypi.org/project/tigrbl-base/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/020_base/tigrbl_base](https://github.com/tigrbl/tigrbl/tree/master/pkgs/020_base/tigrbl_base).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-base`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/020_base/tigrbl_base` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-base?**

Base contract package for Tigrbl apps, routers, tables, sessions, middleware, requests, responses, bindings, and engine interfaces.

**When should I install tigrbl-base?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-base for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-base fit?**

`tigrbl-base` lives at `pkgs/020_base/tigrbl_base` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-base work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-base
```

```bash
pip install tigrbl-base
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-base`](https://pypi.org/project/tigrbl-base/) |
| Repository path | [`pkgs/020_base/tigrbl_base`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/020_base/tigrbl_base) |
| Python import root | `tigrbl_base` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Abstraction Semantics**

`tigrbl-base` is the abstract contract layer between core specs and concrete implementations. It is useful when you need interface behavior without importing the facade or concrete ASGI/application classes.

The package answers questions such as:

- What must an app/router/table expose for assembly?
- How do REST and JSON-RPC maps represent operation bindings?
- What does a request, response, middleware, hook, session, engine provider, or storage adapter need to provide?
- How should column metadata be inferred before a concrete table class lowers it into ORM/schema/runtime behavior?

It should not own route registration side effects, transport IO, database engine construction, or runtime execution. Those belong in `tigrbl-concrete`, engine packages, kernel/runtime packages, or the facade.

**Base Contracts by Area**

| Area | Base responsibility |
|---|---|
| App/router/table | Provide shared assembly, inclusion, registration, and metadata contracts. |
| Operations and bindings | Represent operation maps, REST maps, RPC maps, alias behavior, and binding access. |
| Schema and IO | Provide base shape for request/response/schema objects without deciding concrete rendering. |
| Engine/session/storage | Define provider/session/storage contracts so concrete engines can plug in consistently. |
| Hooks/security/middleware | Provide registration and interface surfaces for lifecycle customization and request policy. |
| Columns | Infer and lower type information while keeping spec-level intent separate from concrete ORM wiring. |

**Column Inference**

`tigrbl_base.column.infer` supports the framework's schema-first and table-first workflows. It helps interpret Python typing, JSON hints, planning metadata, and column options before concrete packages lower them into SQLAlchemy/Pydantic/runtime representations.

Best practices for column inference:
- Keep inference deterministic; the same type hints and config should produce the same plan.
- Keep storage intent separate from wire-schema intent.
- Preserve explicit user configuration over inferred defaults.
- Add tests for ambiguous type handling instead of silently guessing.

**Extension Guidance**

- Depend on `tigrbl-base` when you are writing concrete adapters, engine adapters, or framework tests that need abstract contracts.
- Do not import `tigrbl` facade classes here; base should remain lower than the public facade.
- Keep methods small and contract-oriented. Put operational side effects in concrete implementations or atoms.
- Treat base classes as compatibility surfaces. Renaming or tightening a method affects all concrete packages.
- Prefer composition with `tigrbl-core` specs rather than duplicating spec fields in base classes.

Authoring BCP for this boundary:
- Do use `tigrbl-base` for abstract app/router/table/session/request/response/binding/security/middleware/storage contracts and column inference behavior.
- Do keep column inference deterministic and spec-driven before concrete packages lower intent into ORM, schema, runtime, or docs behavior.
- Do not make `tigrbl-base` the public application import path for normal service code.
- Do not put route registration side effects, direct database transaction calls, concrete engine construction, FastAPI/Starlette route objects, or runtime execution into this package.
- Avoid treating SQLAlchemy materialization as the source of truth here. Base may prepare and validate metadata, but reusable field behavior should remain represented by Tigrbl specs.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-base` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-base` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/020_base/tigrbl_base/NOTICE) for attribution.
<!-- readme-standards:end notices -->
