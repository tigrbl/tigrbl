# tigrbl_engine_mariadb

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_engine_mariadb</strong></p>
<p align="center">MariaDB engine plugin providing native Tigrbl EngineSession integration.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_mariadb/"><img alt="pypi: tigrbl_engine_mariadb" src="https://img.shields.io/pypi/v/tigrbl_engine_mariadb?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml"><img alt="Layer: 90_engines" src="https://img.shields.io/static/v1?label=Layer&amp;message=90_engines&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_mariadb/"><img alt="Monthly PyPI downloads: tigrbl_engine_mariadb" src="https://img.shields.io/pypi/dm/tigrbl_engine_mariadb?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/README.md"><img alt="README hits: tigrbl_engine_mariadb" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/90_engines/tigrbl_engine_mariadb/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

The MariaDB engine plugin for Tigrbl. It registers the `mariadb` engine kind and
returns Tigrbl `EngineSession` instances backed by SQLAlchemy and PyMySQL.

```python
from tigrbl.factories.engine import mariadb

engine = mariadb(user="portwyrm", pwd="secret", name="portwyrm")
```

### Why This Package

Use this project for mariaDB engine plugin providing native Tigrbl EngineSession integration.

### When to Use

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

### Features

- `MariaDBSession`: MariaDB session exposed through Tigrbl's shared EngineSession contract.

### Non-Goals

`tigrbl_engine_mariadb` owns mariaDB engine plugin providing native Tigrbl EngineSession integration. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml) declares runtime dependencies including `sqlalchemy`, `pymysql`, `tigrbl`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_engine_mariadb
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_engine_mariadb
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_engine_mariadb
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/docs/readme/quick_start.py).

```python
from tigrbl.factories.engine import mariadb
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_engine_mariadb` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/docs/readme/usage.py).

```python
from tigrbl.factories.engine import mariadb
```
<!-- readme-standards:end example.usage -->

The walkthrough above is retained. The entry surface can be loaded with:

### Configuration

Configure `tigrbl_engine_mariadb` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/src/tigrbl_engine_mariadb/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_engine_mariadb` source raises `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_engine_mariadb` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `MariaDBSession`, `mariadb_capabilities`, `mariadb_engine`, `register`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

MariaDB engine plugin providing native Tigrbl EngineSession integration.

### Public API and Import Surfaces

MariaDB/MySQL engine registration via tigrbl.engine_plugins. See the project source and existing examples above for supported call signatures.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `mariadb` → `tigrbl_engine_mariadb.plugin:register`
- `tigrbl.engine_plugins` → `mysql` → `tigrbl_engine_mariadb.plugin:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_engine_mariadb` are `sqlalchemy`, `pymysql`, `tigrbl`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/src/tigrbl_engine_mariadb/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_engine_mariadb` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_engine_mariadb`, use the source-declared public interfaces (`MariaDBSession`, `mariadb_capabilities`, `mariadb_engine`, `register`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_engine_mariadb` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_engine_mariadb`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/src/tigrbl_engine_mariadb/__init__.py). The `tigrbl_engine_mariadb` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_engine_mariadb` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_engine_mariadb` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_mariadb_engine.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/tests/test_mariadb_engine.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/src/tigrbl_engine_mariadb/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_engine_mariadb` provides mariaDB engine plugin providing native Tigrbl EngineSession integration; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_engine_mariadb`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/src/tigrbl_engine_mariadb/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_engine_mariadb` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_mariadb)

### Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_mariadb)
- [pypi: tigrbl_engine_mariadb](https://pypi.org/project/tigrbl_engine_mariadb/)
<!-- readme-standards:end project-links -->

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_engine_mariadb`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/90_engines/tigrbl_engine_mariadb` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_engine_mariadb?**

MariaDB engine plugin providing native Tigrbl EngineSession integration.

**When should I install tigrbl_engine_mariadb?**

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

**Who is tigrbl_engine_mariadb for?**

Tigrbl maintainers and application developers working with this project’s APIs.

**Where does tigrbl_engine_mariadb fit?**

Source: `pkgs/90_engines/tigrbl_engine_mariadb` in the Tigrbl workspace.

**How does tigrbl_engine_mariadb work?**

MariaDB/MySQL engine registration via tigrbl.engine_plugins. The examples and implementation above describe the configuration and execution flow.

**Install**

From the repository root:

```console
uv sync --project pkgs/90_engines/tigrbl_engine_mariadb
```

**Surface Coverage**

| Surface | Value |
| --- | --- |
| Project | `tigrbl_engine_mariadb` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_engine_mariadb` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_engine_mariadb` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_engine_mariadb` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/LICENSE).
<!-- readme-standards:end license -->

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_mariadb/NOTICE) for attribution.
<!-- readme-standards:end notices -->
