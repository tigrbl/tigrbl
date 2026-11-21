# tigrbl-examples

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-examples</strong></p>
<p align="center">Packaged Tigrbl example modules migrated from the test support package.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-examples/"><img alt="pypi: tigrbl-examples" src="https://img.shields.io/pypi/v/tigrbl-examples"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml"><img alt="Layer: 96_examples" src="https://img.shields.io/static/v1?label=Layer&amp;message=96_examples&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-examples/"><img alt="Monthly PyPI downloads: tigrbl-examples" src="https://img.shields.io/pypi/dm/tigrbl-examples"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/README.md"><img alt="README hits: tigrbl-examples" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/96_examples/tigrbl_examples/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-examples`: Packaged Tigrbl example modules migrated from the test support package.

### Why This Package

Use it when examples need a package boundary separate from pytest fixtures and conformance helper utilities.

### When to Use

Choose `tigrbl-examples` when you need importable example modules. Choose [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) when you need reusable test helpers, fixtures, and conformance assertions.

### Features

- `BaseWidget`: declared in tigrbl_examples/08-intermediate-config/test_08_05_dynamic_engine_choice.py
- `WidgetSpec`: Reusable configuration for widgets stored in PostgreSQL.
- `Widget`: declared in tigrbl_examples/08-intermediate-config/test_08_05_dynamic_engine_choice.py
- `Widget`: declared in tigrbl_examples/08-intermediate-config/test_08_06_factory_method_patterns.py
- `Status`: declared in tigrbl_examples/14-advanced-column-types/test_14_04_postgres_types.py

### Non-Goals

`tigrbl-examples` owns packaged Tigrbl example modules migrated from the test support package. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml) declares runtime dependencies including `tigrbl`, `tigrbl-client`, `httpx`, `pytest`, `pytest-asyncio`, `uvicorn`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-examples
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-examples
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-examples
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/docs/readme/quick_start.py).

```python
import tigrbl_examples

print(tigrbl_examples.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-examples` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/docs/readme/usage.py).

```python
import tigrbl_examples

print(tigrbl_examples.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-examples
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-examples"))
PY
```

**Import the package boundary**


**Import shared example helpers**

```python
from tigrbl_examples._support import pick_unique_port

print(pick_unique_port())
```

**Run the migrated example tests**

```bash
uv run pytest pkgs/96_examples/tigrbl_examples/tigrbl_examples -q
```

### Configuration

Configure `tigrbl-examples` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/tigrbl_examples/06_intermediate_ops/test_01_op_ctx.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-examples` source raises `AssertionError`, `HTTPException`, `RuntimeError`, `SystemExit`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-examples` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `BaseWidget`, `WidgetSpec`, `Widget`, `Widget`, `Status`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-examples` owns the `example package` boundary. It does not own conformance assertions, package validation policy, or reusable pytest harness internals.

Implementation orientation:
- `tigrbl_examples`: migrated beginner, intermediate, advanced, and expert example modules plus shared example helpers.

This README is the package-local distribution entry point for `tigrbl-examples`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_examples`.
- Public symbols: public surface is module-oriented; import the needed example module or helper directly.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl_client`](https://pypi.org/project/tigrbl_client/).
- External runtime dependencies: `httpx>=0.27.0,<0.28`, `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `uvicorn`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-examples` are `tigrbl`, `tigrbl-client`, `httpx`, `pytest`, `pytest-asyncio`, `uvicorn`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/tigrbl_examples/06_intermediate_ops/test_01_op_ctx.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tigrbl_tests`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-examples`, use the source-declared public interfaces (`BaseWidget`, `WidgetSpec`, `Widget`, `Widget`, `Status`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-examples` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-examples`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/tigrbl_examples/06_intermediate_ops/test_01_op_ctx.py). The `tigrbl-examples` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-examples` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-examples` package directory for the maintained example source checks (Python compilation and non-Python file presence). Behavioral tests may live in the repository’s shared suites; the new README syntax test is not presented as runtime coverage for packaged Tigrbl example modules migrated from the test support package.

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/tigrbl_examples/06_intermediate_ops/test_01_op_ctx.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-examples` provides packaged Tigrbl example modules migrated from the test support package; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-examples`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/tigrbl_examples/06_intermediate_ops/test_01_op_ctx.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-examples` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

### Related Packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)
- [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/tigrbl_examples)
- [pypi: tigrbl-examples](https://pypi.org/project/tigrbl-examples/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/96_examples/tigrbl_examples](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/tigrbl_examples).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-examples`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/96_examples/tigrbl_examples` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-examples?**

Packaged Tigrbl example modules migrated from the test support package.

**When should I install tigrbl-examples?**

Install it for runnable example modules, documentation checks, and integration tests that import shared example helpers.

**Who is tigrbl-examples for?**

Maintainers, extension authors, and documentation workflows that need importable Tigrbl examples.

**Where does tigrbl-examples fit?**

`tigrbl-examples` lives at `pkgs/96_examples/tigrbl_examples` and owns the migrated example module tree previously carried by `tigrbl_tests`.

**How does tigrbl-examples work?**

It exposes example modules directly under the `tigrbl_examples` import root so callers import `tigrbl_examples.<module>` without an extra nested examples namespace.

**Start here**

Read the beginner app lessons in this order:

1. [App initialization](tigrbl_examples/05_beginner_app_api/test_01_tigrbl_app_init.py) registers a model and initializes the app.
2. [Router composition](tigrbl_examples/05_beginner_app_api/test_02_app_router.py) attaches a router and checks the registered routes.
3. [JSON-RPC mounting](tigrbl_examples/05_beginner_app_api/test_03_jsonrpc_mount.py) mounts a JSON-RPC endpoint at `/rpc` while preserving existing routes.

Run only these three lessons from the repository root:

```sh
uv run --frozen --package tigrbl-examples python -m pytest -q \
  pkgs/96_examples/tigrbl_examples/tigrbl_examples/05_beginner_app_api/test_01_tigrbl_app_init.py \
  pkgs/96_examples/tigrbl_examples/tigrbl_examples/05_beginner_app_api/test_02_app_router.py \
  pkgs/96_examples/tigrbl_examples/tigrbl_examples/05_beginner_app_api/test_03_jsonrpc_mount.py
```

**Tigrbl Skills for Codex**

Use [Tigrbl Skills](https://github.com/tigrbl/tigrbl-skills) alongside the
examples for guidance on setting up an app, composing routers, and mounting
protocol bindings. The lessons above run independently.

Access to the source repository requires GitHub permission. In that repository,
the Codex marketplace manifest is at .agents/plugins/marketplace.json.

**Install**

```bash
uv add tigrbl-examples
```

```bash
pip install tigrbl-examples
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-examples`](https://pypi.org/project/tigrbl-examples/) |
| Repository path | [`pkgs/96_examples/tigrbl_examples`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/tigrbl_examples) |
| Python import root | `tigrbl_examples` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-examples` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-examples` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/tigrbl_examples/NOTICE) for attribution.
<!-- readme-standards:end notices -->
