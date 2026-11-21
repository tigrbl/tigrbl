# tigrbl-ops-olap

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-ops-olap</strong></p>
<p align="center">Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-ops-olap/"><img alt="pypi: tigrbl-ops-olap" src="https://img.shields.io/pypi/v/tigrbl-ops-olap"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml"><img alt="Layer: 60_ops" src="https://img.shields.io/static/v1?label=Layer&amp;message=60_ops&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-ops-olap/"><img alt="Monthly PyPI downloads: tigrbl-ops-olap" src="https://img.shields.io/pypi/dm/tigrbl-ops-olap"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/README.md"><img alt="README hits: tigrbl-ops-olap" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/60_ops/tigrbl_ops_olap/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-ops-olap`: Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.

### Why This Package

Use it when you need this operation-family boundary directly instead of consuming operations through the top-level facade.

### When to Use

Choose `tigrbl-ops-olap` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- Public source surface: `aggregate`, `group_by`.
- Declared responsibility: Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.
- Versioned package metadata and maintained checkout examples.

### Non-Goals

`tigrbl-ops-olap` owns analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml) declares no direct runtime dependencies. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-ops-olap
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-ops-olap
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-ops-olap
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_ops_olap")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-ops-olap` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_ops_olap")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-ops-olap
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-ops-olap"))
PY
```

**Import the package boundary**


**Import a public symbol**

```python
from tigrbl_ops_olap import aggregate

print(aggregate)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-ops-olap
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl-ops-olap` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tigrbl_ops_olap/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-ops-olap` source raises `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-ops-olap` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `aggregate`, `group_by`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-ops-olap` owns the `operation-family package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_ops_olap`: ops

This README is the package-local distribution entry point for `tigrbl-ops-olap`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_ops_olap`.
- Public symbols: `aggregate`, `group_by`.
- Workspace dependencies: none declared.
- External runtime dependencies: none declared.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-ops-olap` are empty in the manifest. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tigrbl_ops_olap/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-atoms`, `tigrbl-concrete`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-ops-olap`, use the source-declared public interfaces (`aggregate`, `group_by`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-ops-olap` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-ops-olap`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tigrbl_ops_olap/__init__.py). The `tigrbl-ops-olap` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-ops-olap` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-ops-olap` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_smoke.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tests/test_smoke.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tigrbl_ops_olap/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-ops-olap` provides analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-ops-olap`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/tigrbl_ops_olap/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-ops-olap` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/60_ops/tigrbl_ops_olap)
- [pypi: tigrbl-ops-olap](https://pypi.org/project/tigrbl-ops-olap/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/60_ops/tigrbl_ops_olap](https://github.com/tigrbl/tigrbl/tree/master/pkgs/60_ops/tigrbl_ops_olap).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-ops-olap`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/60_ops/tigrbl_ops_olap` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-ops-olap?**

Analytical OLAP operation boundaries for Tigrbl workloads, query-oriented APIs, and engine integrations.

**When should I install tigrbl-ops-olap?**

Install it for framework internals, extension packages, or focused tests that target this operation plane.

**Who is tigrbl-ops-olap for?**

Framework maintainers and extension authors working near Tigrbl operation dispatch.

**Where does tigrbl-ops-olap fit?**

`tigrbl-ops-olap` lives at `pkgs/60_ops/tigrbl_ops_olap` and serves focused operation dispatch behavior inside the Tigrbl runtime model.

**How does tigrbl-ops-olap work?**

It contributes operation handlers and dispatch-facing primitives consumed by the facade, runtime, and kernel layers.

**Install**

```bash
uv add tigrbl-ops-olap
```

```bash
pip install tigrbl-ops-olap
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/) |
| Repository path | [`pkgs/60_ops/tigrbl_ops_olap`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/60_ops/tigrbl_ops_olap) |
| Python import root | `tigrbl_ops_olap` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-ops-olap` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-ops-olap` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/60_ops/tigrbl_ops_olap/NOTICE) for attribution.
<!-- readme-standards:end notices -->
