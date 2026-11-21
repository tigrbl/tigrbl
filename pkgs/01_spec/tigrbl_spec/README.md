# tigrbl_spec

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_spec</strong></p>
<p align="center">Shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_spec/"><img alt="pypi: tigrbl_spec" src="https://img.shields.io/pypi/v/tigrbl_spec"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml"><img alt="Layer: 01_spec" src="https://img.shields.io/static/v1?label=Layer&amp;message=01_spec&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;color=525252"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_spec/"><img alt="Monthly PyPI downloads: tigrbl_spec" src="https://img.shields.io/pypi/dm/tigrbl_spec"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/README.md"><img alt="README hits: tigrbl_spec" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/01_spec/tigrbl_spec/README.md.svg?label=README%20hits"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;color=525252"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;color=525252"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_spec`: Shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl_spec` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `CodegenFreshnessError`: Raised when checked-in generated models do not match packaged schemas.
- `SchemaMigrationError`: Raised when no valid schema catalog migration path exists.
- `SpecDataclass`: declared in tigrbl_spec/models/v0_3_20/__init__.py
- `SpecSchemaError`: Base error for tigrbl_spec schema catalog failures.
- `UnknownSpecKindError`: Raised when a payload references an unknown spec kind.
- `UnsupportedSchemaVersionError`: Raised when a catalog version is not packaged or supported.
- `SpecValidationError`: Raised when a spec payload does not satisfy its schema.

### Non-Goals

`tigrbl_spec` owns shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml) declares runtime dependencies including `jsonschema`, `typing-extensions`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_spec
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_spec
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_spec
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_spec")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_spec` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_spec")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl_spec
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_spec"))
PY
```

**Import the package boundary**


**Import a public symbol**

```python
from tigrbl_spec import __version__

print(__version__)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl_spec
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl_spec` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tigrbl_spec/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_spec` source raises `CodegenFreshnessError`, `FileNotFoundError`, `SchemaMigrationError`, `SpecValidationError`, `UnknownSpecKindError`, `UnsupportedSchemaVersionError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_spec` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CURRENT_SCHEMA_VERSION`, `SCHEMA_VERSION`, `SpecSchemaError`, `SpecValidationError`, `UnknownSpecKindError`, `UnsupportedSchemaVersionError`, `__version__`, `identity_fields`, `load_bundle`, `load_manifest`, `load_payload`, `load_schema`, `schema_path`, `schema_versions`, `spec_kinds`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl_spec` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- Module layout is intentionally small or namespace-oriented.

This README is the package-local distribution entry point for `tigrbl_spec`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_spec`.
- Public symbols: `__version__`.
- Workspace dependencies: none declared.
- External runtime dependencies: none declared.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_spec` are `jsonschema`, `typing-extensions`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tigrbl_spec/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tigrbl-core`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl_spec`, use the source-declared public interfaces (`CURRENT_SCHEMA_VERSION`, `SCHEMA_VERSION`, `SpecSchemaError`, `SpecValidationError`, `UnknownSpecKindError`, `UnsupportedSchemaVersionError`, `__version__`, `identity_fields`, `load_bundle`, `load_manifest`, `load_payload`, `load_schema`, `schema_path`, `schema_versions`, `spec_kinds`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_spec` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_spec`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tigrbl_spec/__init__.py). The `tigrbl_spec` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_spec` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_spec` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/unit/test_codegen_freshness.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tests/unit/test_codegen_freshness.py)
- [tests/unit/test_generated_models.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tests/unit/test_generated_models.py)
- [tests/unit/test_generated_model_corpus_t2.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tests/unit/test_generated_model_corpus_t2.py)
- [tests/unit/test_headers_spec_catalog_t2.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tests/unit/test_headers_spec_catalog_t2.py)
- [tests/unit/test_migrations.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tests/unit/test_migrations.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tigrbl_spec/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_spec` provides shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_spec`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/tigrbl_spec/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_spec` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/01_spec/tigrbl_spec)
- [pypi: tigrbl_spec](https://pypi.org/project/tigrbl_spec/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/01_spec/tigrbl_spec](https://github.com/tigrbl/tigrbl/tree/master/pkgs/01_spec/tigrbl_spec).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_spec`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/01_spec/tigrbl_spec` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.1` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_spec?**

Shared Tigrbl interfaces, protocol definitions, compatibility targets, and specification artifacts for framework integration.

**When should I install tigrbl_spec?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl_spec for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl_spec fit?**

`tigrbl_spec` lives at `pkgs/01_spec/tigrbl_spec` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl_spec work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl_spec
```

```bash
pip install tigrbl_spec
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_spec`](https://pypi.org/project/tigrbl_spec/) |
| Repository path | [`pkgs/01_spec/tigrbl_spec`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/01_spec/tigrbl_spec) |
| Python import root | `tigrbl_spec` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_spec` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_spec` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/01_spec/tigrbl_spec/NOTICE) for attribution.
<!-- readme-standards:end notices -->
