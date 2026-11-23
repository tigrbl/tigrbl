# tigrbl_engine_rom

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_engine_rom</strong></p>
<p align="center">Immutable read-only memory engine plugin for Tigrbl.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_rom/"><img alt="pypi: tigrbl_engine_rom" src="https://img.shields.io/pypi/v/tigrbl_engine_rom?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml"><img alt="Layer: 90_engines" src="https://img.shields.io/static/v1?label=Layer&amp;message=90_engines&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_engine_rom/"><img alt="Monthly PyPI downloads: tigrbl_engine_rom" src="https://img.shields.io/pypi/dm/tigrbl_engine_rom?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/README.md"><img alt="README hits: tigrbl_engine_rom" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/90_engines/tigrbl_engine_rom/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_engine_rom`: Immutable read-only memory engine plugin for Tigrbl.

### Why This Package

Use it for embedded catalogs, fixtures, policy data, reference tables, and other datasets that must never change at runtime.

### When to Use

Choose ROM for immutable embedded data. Choose `tigrbl_engine_inmemory` when transactions and runtime writes are required.

### Features

- `ROMEngine`: Process-local immutable row image bound as an input to one table.
- `ROMResult`: Small result facade compatible with Tigrbl's scalar query helpers.
- `ROMSession`: Async Tigrbl session over an immutable :class:`ROMEngine` snapshot.

### Non-Goals

`tigrbl_engine_rom` owns immutable read-only memory engine plugin for Tigrbl. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml) declares runtime dependencies including `tigrbl`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_engine_rom
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_engine_rom
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_engine_rom
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/docs/readme/quick_start.py).

```python
from tigrbl_engine_rom import build_rom

engine, sessionmaker = build_rom(
    mapping={
        "rows": [
            {"code": "US", "name": "United States"},
            {"code": "CA", "name": "Canada"},
        ],
        "primary_key": "code",
    }
)

session = sessionmaker()
assert session.get_row("CA")["name"] == "Canada"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_engine_rom` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/docs/readme/usage.py).

```python
from tigrbl_engine_rom import build_rom

engine, sessionmaker = build_rom(
    mapping={
        "rows": [
            {"code": "US", "name": "United States"},
            {"code": "CA", "name": "Canada"},
        ],
        "primary_key": "code",
    }
)

session = sessionmaker()
assert session.get_row("CA")["name"] == "Canada"
```
<!-- readme-standards:end example.usage -->

Bind the engine configuration into a table:

```python
from tigrbl.factories.table import defineTableSpec

class CountrySpec(defineTableSpec(engine={
    "kind": "rom",
    "rows": [
        {"code": "US", "name": "United States"},
        {"code": "CA", "name": "Canada"},
    ],
    "primary_key": "code",
})):
    pass
```

### Configuration

Configure `tigrbl_engine_rom` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/src/tigrbl_engine_rom/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_engine_rom` source raises `NotImplementedError`, `RuntimeError`, `TypeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_engine_rom` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `READ_ONLY_ERROR`, `ROMEngine`, `ROMResult`, `ROMSession`, `__version__`, `build_rom`, `capabilities`, `register`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

The package owns the ROM image, read-only session, plugin registration, and scalar result facade.

### Public API and Import Surfaces

Public symbols are `ROMEngine`, `ROMSession`, `ROMResult`, `build_rom`, `capabilities`, and `register`.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `tigrbl.engine_plugins` → `rom` → `tigrbl_engine_rom.plugin:register`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_engine_rom` are `tigrbl`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/src/tigrbl_engine_rom/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_engine_rom` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_engine_rom`, use the source-declared public interfaces (`READ_ONLY_ERROR`, `ROMEngine`, `ROMResult`, `ROMSession`, `__version__`, `build_rom`, `capabilities`, `register`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_engine_rom` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_engine_rom`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/src/tigrbl_engine_rom/__init__.py). The `tigrbl_engine_rom` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_engine_rom` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_engine_rom` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_rom_engine.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/tests/test_rom_engine.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

The package is implemented with package-local behavioral tests. Certification remains governed by the repository SSOT registry and release workflows.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/src/tigrbl_engine_rom/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_engine_rom` provides immutable read-only memory engine plugin for Tigrbl; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_engine_rom`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/src/tigrbl_engine_rom/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_engine_rom` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](../../../docs/README.md)
- [Package catalog](../../../docs/developer/PACKAGE_CATALOG.md)
- [SSOT registry](../../../.ssot/registry.json)

### Related Packages

- `tigrbl`
- `tigrbl_engine_inmemory`
- `tigrbl_engine_memkv`

### Project Links

<!-- readme-standards:begin project-links -->
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/90_engines/tigrbl_engine_rom)
- [pypi: tigrbl_engine_rom](https://pypi.org/project/tigrbl_engine_rom/)
<!-- readme-standards:end project-links -->

- [Discord](https://discord.gg/K4YTAPapjR)
- [GitHub issues](https://github.com/tigrbl/tigrbl/issues)

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_engine_rom`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/90_engines/tigrbl_engine_rom` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_engine_rom?**

`tigrbl_engine_rom` loads one mapping-backed row image and serves it through Tigrbl's engine-session contract. The engine configuration is bound as an input to a table.

**When should I install tigrbl_engine_rom?**

Install it when your application needs fast reads from a fixed memory image and should fail closed on every write.

**Who is tigrbl_engine_rom for?**

It is for application developers shipping trusted reference data or deterministic read-only test images.

**Where does tigrbl_engine_rom fit?**

It is a standalone package under `pkgs/90_engines` and is discovered through the `tigrbl.engine` entry-point group as kind `rom`.

**How does tigrbl_engine_rom work?**

`ROMEngine` subclasses Tigrbl's `EngineBase`. Construction validates the bound table's rows and primary key, deeply detaches the source data, and freezes it. Reads always return caller-owned copies. Sessions force `read_only=True`, even if a caller requests otherwise.

**Install**

```bash
uv add tigrbl_engine_rom
```

**Surface Coverage**

| Surface | Value |
|---|---|
| Engine kind | `rom` |
| Python import | `tigrbl_engine_rom` |
| Entry point | `tigrbl.engine` |
| Persistence | process-local immutable memory |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_engine_rom` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_engine_rom` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/90_engines/tigrbl_engine_rom/NOTICE) for attribution.
<!-- readme-standards:end notices -->
