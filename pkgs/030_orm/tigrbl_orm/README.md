# tigrbl-orm

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-orm</strong></p>
<p align="center">SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-orm/"><img alt="pypi: tigrbl-orm" src="https://img.shields.io/pypi/v/tigrbl-orm?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml"><img alt="Source version: 0.4.6.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml"><img alt="Layer: 030_orm" src="https://img.shields.io/static/v1?label=Layer&amp;message=030_orm&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-orm/"><img alt="Monthly PyPI downloads: tigrbl-orm" src="https://img.shields.io/pypi/dm/tigrbl-orm?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/README.md"><img alt="README hits: tigrbl-orm" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/030_orm/tigrbl_orm/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-orm`: SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-orm` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- Public source surface: the checkout commands documented in Quick Start.
- Declared responsibility: SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-orm` owns sQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml) declares runtime dependencies including `sqlalchemy`. Use the source-checkout workflow for this workspace or test harness.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-orm
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-orm
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-orm
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_orm.orm")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-orm` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_orm.orm")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-orm
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-orm"))
PY
```

**Import the package boundary**


**Inspect available modules**

```python
import importlib
import pkgutil

module = importlib.import_module("tigrbl_orm.orm")
for info in pkgutil.iter_modules(getattr(module, "__path__", [])):
    print(info.name)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-orm
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl-orm` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-orm` source does not establish a package-wide exception hierarchy. Preserve errors from its declared dependencies and validate inputs using the specific public contract in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml).

### Best Practices

Use the explicit `tigrbl-orm` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing the checkout commands documented in Quick Start; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-orm` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_orm`: orm/

This README is the package-local distribution entry point for `tigrbl-orm`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_orm`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: none declared.
- External runtime dependencies: `sqlalchemy>=2.0`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-orm` are `sqlalchemy`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-ops-oltp`, `tigrbl`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-orm`, use the source-declared public interfaces (the checkout commands documented in Quick Start) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-orm` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-orm`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml). The `tigrbl-orm` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-orm` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-orm` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_smoke.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/tests/test_smoke.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/210_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-orm` provides sQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-orm`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-orm` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

### Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/030_orm/tigrbl_orm)
- [pypi: tigrbl-orm](https://pypi.org/project/tigrbl-orm/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/030_orm/tigrbl_orm](https://github.com/tigrbl/tigrbl/tree/master/pkgs/030_orm/tigrbl_orm).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-orm`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/030_orm/tigrbl_orm` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-orm?**

SQLAlchemy ORM tables, mixins, columns, model helpers, and persistence primitives for Tigrbl applications.

**When should I install tigrbl-orm?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-orm for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-orm fit?**

`tigrbl-orm` lives at `pkgs/030_orm/tigrbl_orm` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-orm work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-orm
```

```bash
pip install tigrbl-orm
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/) |
| Repository path | [`pkgs/030_orm/tigrbl_orm`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/030_orm/tigrbl_orm) |
| Python import root | `tigrbl_orm` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

**Convenient Authoring Path and Best Current Practice (BCP)**

`tigrbl-orm` is the SQLAlchemy-facing implementation boundary for Tigrbl table and persistence helpers. Normal application documentation should still lead with the `tigrbl` facade, Tigrbl table/column helpers, and Tigrbl specs.

**Keep ORM usage boundary-owned**

- Avoid: Exposing implementation-only ORM helpers as facade-level guidance unless the package boundary is explicit.
- Do: Use this package when implementing or testing ORM helpers, table mixins, persistence primitives, and SQLAlchemy-facing compatibility behavior.
- Why: SQLAlchemy is useful inside the storage boundary, while application users still get the more convenient Tigrbl facade contract.

**Keep specs authoritative before ORM materialization**

- Avoid: Duplicating field behavior across ORM declarations and Tigrbl specs.
- Do: Keep ORM behavior aligned with Tigrbl table, column, datatype, storage, IO, and operation specs.
- Why: The spec layer is the reusable source for behavior that must project into storage, validation, runtime, hooks, diagnostics, and docs.

**Do not teach raw ORM declarations as application style**

- Do not: Present raw SQLAlchemy `mapped_column(...)` or `Column(...)` as the preferred application authoring surface when Tigrbl column helpers or specs can express the behavior.
- Do: Let Tigrbl specs describe reusable field and operation intent before ORM materialization.
- Why: Raw ORM declarations are only one lowering target and cannot carry the full Tigrbl storage, IO, validation, docs, hook, and runtime contract.

**Do not move application behavior into this boundary**

- Do not: Put application route authoring, FastAPI/Starlette route objects, ad-hoc engine construction in handlers, or direct transaction control in this package's public examples.
- Do: Keep application-facing examples on the `tigrbl` facade and keep this README focused on the ORM implementation boundary.
- Why: This keeps routes, engines, transactions, schemas, hooks, diagnostics, and runtime planning owned by the packages that govern those behaviors.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-orm` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-orm` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/030_orm/tigrbl_orm/NOTICE) for attribution.
<!-- readme-standards:end notices -->
