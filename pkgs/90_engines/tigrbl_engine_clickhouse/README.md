# tigrbl_engine_clickhouse

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_engine_clickhouse</strong></p>
<p align="center">ClickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_clickhouse/"><img alt="pypi: tigrbl_engine_clickhouse" src="https://img.shields.io/pypi/v/tigrbl_engine_clickhouse"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml"><img alt="Layer: 90_engines" src="https://img.shields.io/static/v1?label=Layer&amp;message=90_engines&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_clickhouse/"><img alt="Monthly PyPI downloads: tigrbl_engine_clickhouse" src="https://img.shields.io/pypi/dm/tigrbl_engine_clickhouse"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/README.md"><img alt="README hits: tigrbl_engine_clickhouse" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/90_engines/tigrbl_engine_clickhouse/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_engine_clickhouse`: ClickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration.

### Why This Package

Use it when a Tigrbl application needs this backend without installing every engine package.

### When to Use

Choose `tigrbl_engine_clickhouse` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `ClickHouseEngine`: Thin handle for ClickHouse connectivity parameters.
- `ClickHouseSession`: A Tigrbl session backed by clickhouse-connect (sync client).

### Non-Goals

`tigrbl_engine_clickhouse` owns clickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml) declares runtime dependencies including `tigrbl`, `clickhouse-connect`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_engine_clickhouse
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_engine_clickhouse
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_engine_clickhouse
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/docs/readme/quick_start.py).

```python
from tigrbl_engine_clickhouse import register

register()
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_engine_clickhouse` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/docs/readme/usage.py).

```python
from tigrbl_engine_clickhouse import register

register()
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl_engine_clickhouse
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_engine_clickhouse"))
PY
```

**Register the engine plugin explicitly**


**Discover the engine through package metadata**

```python
from importlib.metadata import entry_points

for entry_point in entry_points(group="tigrbl.engine"):
    if entry_point.module.startswith("tigrbl_engine_clickhouse"):
        plugin_register = entry_point.load()
        plugin_register()
```

**Install alongside the facade**

```bash
uv add tigrbl tigrbl_engine_clickhouse
pip install tigrbl tigrbl_engine_clickhouse
```

### Configuration

Configure `tigrbl_engine_clickhouse` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_engine_clickhouse` source raises `NotImplementedError`, `RuntimeError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_engine_clickhouse` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `ClickHouseEngine`, `ClickHouseSession`, `clickhouse_engine`, `register`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl_engine_clickhouse` owns the `engine plugin` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_engine_clickhouse`: engine, session

This README is the package-local distribution entry point for `tigrbl_engine_clickhouse`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_engine_clickhouse`.
- Public symbols: `ClickHouseEngine`, `ClickHouseSession`, `clickhouse_engine`, `register`.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/).
- External runtime dependencies: `clickhouse-connect>=0.6.0`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `clickhouse` → `tigrbl_engine_clickhouse:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_engine_clickhouse` are `tigrbl`, `clickhouse-connect`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_engine_clickhouse` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_engine_clickhouse`, use the source-declared public interfaces (`ClickHouseEngine`, `ClickHouseSession`, `clickhouse_engine`, `register`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_engine_clickhouse` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_engine_clickhouse`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/__init__.py). The `tigrbl_engine_clickhouse` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_engine_clickhouse` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_engine_clickhouse` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_smoke.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/tests/test_smoke.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_engine_clickhouse` provides clickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_engine_clickhouse`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/src/tigrbl_engine_clickhouse/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_engine_clickhouse` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_clickhouse)
- [pypi: tigrbl_engine_clickhouse](https://pypi.org/project/tigrbl_engine_clickhouse/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/90_engines/tigrbl_engine_clickhouse](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_clickhouse).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_engine_clickhouse`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/90_engines/tigrbl_engine_clickhouse` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_engine_clickhouse?**

ClickHouse engine plugin for analytical database sessions, warehouse workloads, and Tigrbl engine registration.

**When should I install tigrbl_engine_clickhouse?**

Install it when the storage, analytics, cache, or integration workload named by this package is the intended runtime backend.

**Who is tigrbl_engine_clickhouse for?**

Application developers, data platform engineers, and operators choosing concrete persistence or data-plane behavior.

**Where does tigrbl_engine_clickhouse fit?**

`tigrbl_engine_clickhouse` lives at `pkgs/90_engines/tigrbl_engine_clickhouse` and serves ClickHouse analytical workloads.

**How does tigrbl_engine_clickhouse work?**

It exposes a `tigrbl.engine` entry point and a package `register()` hook so Tigrbl can discover or load the backend at runtime.

**Install**

```bash
uv add tigrbl_engine_clickhouse
```

```bash
pip install tigrbl_engine_clickhouse
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_engine_clickhouse`](https://pypi.org/project/tigrbl_engine_clickhouse/) |
| Repository path | [`pkgs/90_engines/tigrbl_engine_clickhouse`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_clickhouse) |
| Python import root | `tigrbl_engine_clickhouse` |
| Console scripts | none declared |
| Entry points | `tigrbl.engine` |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_engine_clickhouse` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_engine_clickhouse` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_clickhouse/NOTICE) for attribution.
<!-- readme-standards:end notices -->
