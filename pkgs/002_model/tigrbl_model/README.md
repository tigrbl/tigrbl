# tigrbl_model

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_model</strong></p>
<p align="center">Pydantic-independent validation, serialization, and JSON Schema models for Tigrbl.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_model/"><img alt="pypi: tigrbl_model" src="https://img.shields.io/pypi/v/tigrbl_model?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml"><img alt="Layer: 002_model" src="https://img.shields.io/static/v1?label=Layer&amp;message=002_model&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_model/"><img alt="Monthly PyPI downloads: tigrbl_model" src="https://img.shields.io/pypi/dm/tigrbl_model?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/README.md"><img alt="README hits: tigrbl_model" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/002_model/tigrbl_model/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_model`: Pydantic-independent validation, serialization, and JSON Schema models for Tigrbl.

### Why This Package

Use it when code needs the Pydantic v2 surface validated by the package tests for Tigrbl without taking a runtime dependency on Pydantic.

### When to Use

Choose `tigrbl_model` for the focused model and serialization boundary. Choose the `tigrbl` facade when building a complete API application. Keep Pydantic installed only when independently comparing behavior during development.

### Features

- `ConfigDict`: Dictionary configuration compatible with Tigrbl's Pydantic usage.
- `ErrorDetails`: One validation failure with a stable location and machine-readable type.
- `ValidationError`: Aggregate validation failures for a model operation.
- `ModelUserError`: Raised when a declaration uses a removed or unsupported model option.
- `AliasChoices`: Ordered validation aliases; the first present alias wins.
- `FieldInfo`: Runtime metadata for one declared model field.
- `JsonMixin`: declared in tigrbl_model/mixins/json.py
- `SerdeMixin`: declared in tigrbl_model/mixins/serde.py

### Non-Goals

`tigrbl_model` owns pydantic-independent validation, serialization, and JSON Schema models for Tigrbl. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml) declares runtime dependencies including `pyyaml`, `tomli-w`, `tomli`, `typing-extensions`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_model
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_model
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_model
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/docs/readme/quick_start.py).

```python
from tigrbl_model import Field, Model


class Widget(Model):
    name: str
    quantity: int = Field(default=0, ge=0)


widget = Widget.model_validate_json('{"name":"bolt","quantity":2}')
assert widget.model_dump() == {"name": "bolt", "quantity": 2}
assert Widget.model_validate_yaml(widget.model_dump_yaml()) == widget
assert Widget.model_validate_toml(widget.model_dump_toml()) == widget
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_model` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/docs/readme/usage.py).

```python
from tigrbl_model import Field, Model


class Widget(Model):
    name: str
    quantity: int = Field(default=0, ge=0)


widget = Widget.model_validate_json('{"name":"bolt","quantity":2}')
assert widget.model_dump() == {"name": "bolt", "quantity": 2}
assert Widget.model_validate_yaml(widget.model_dump_yaml()) == widget
assert Widget.model_validate_toml(widget.model_dump_toml()) == widget
```
<!-- readme-standards:end example.usage -->

Plain dataclasses can inherit `SerdeMixin` when validation and schema-model behavior are unnecessary.

### Configuration

Configure `tigrbl_model` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tigrbl_model/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_model` source raises `ModelUserError`, `TypeError`, `ValidationError`, `_issue`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_model` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `AliasChoices`, `BaseModel`, `ConfigDict`, `ErrorDetails`, `Field`, `FieldInfo`, `JsonMixin`, `Model`, `ModelConfig`, `ModelUserError`, `PydanticUndefined`, `RootModel`, `SerdeMixin`, `TomlMixin`, `Undefined`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

- Runtime model construction and field metadata.
- Annotation-driven validation and structured errors.
- Dictionary and JSON serialization.
- JSON Schema generation.
- Independently composable JSON, YAML, and TOML mixins.
- `SerdeMixin`, which aggregates all three format mixins.

### Public API and Import Surfaces

The primary imports are `Model`/`BaseModel`, `RootModel`, `Field`, `ConfigDict`, `ValidationError`, `create_model`, `field_validator`, `model_validator`, and the four serialization mixins. See `tigrbl_model.__all__` for the complete supported surface.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_model` are `pyyaml`, `tomli-w`, `tomli`, `typing-extensions`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tigrbl_model/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_model` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_model`, use the source-declared public interfaces (`AliasChoices`, `BaseModel`, `ConfigDict`, `ErrorDetails`, `Field`, `FieldInfo`, `JsonMixin`, `Model`, `ModelConfig`, `ModelUserError`, `PydanticUndefined`, `RootModel`, `SerdeMixin`, `TomlMixin`, `Undefined`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_model` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_model`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tigrbl_model/__init__.py). The `tigrbl_model` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_model` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_model` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/contracts/test_dynamic_models.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tests/contracts/test_dynamic_models.py)
- [tests/contracts/test_tigrbl_patterns.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tests/contracts/test_tigrbl_patterns.py)
- [tests/json_schema/test_json_schema.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tests/json_schema/test_json_schema.py)
- [tests/parity/test_pydantic_parity.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tests/parity/test_pydantic_parity.py)
- [tests/parity/test_tigrbl_usage_inventory.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tests/parity/test_tigrbl_usage_inventory.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

The package's automated suite compares the supported contract with Pydantic v2 and scans first-party Tigrbl runtime usage. `PARITY.md` records intentional boundaries; Pydantic is a development-only parity oracle and is not a runtime dependency.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tigrbl_model/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_model` provides pydantic-independent validation, serialization, and JSON Schema models for Tigrbl; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_model`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/tigrbl_model/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_model` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Supported parity boundary](PARITY.md)
- [Workspace documentation](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)

### Related Packages

- `tigrbl`
- `tigrbl-core`
- `tigrbl-base`
- `tigrbl-runtime`

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/002_model/tigrbl_model)
- [pypi: tigrbl_model](https://pypi.org/project/tigrbl_model/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR)
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_model`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/002_model/tigrbl_model` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_model?**

`tigrbl_model` is Tigrbl's Pydantic-independent model engine. It owns field metadata, validation, serialization, dynamic model construction, forward-reference rebuilding, and JSON Schema generation.

**When should I install tigrbl_model?**

Install it when building Tigrbl extensions, reusable schema models, or applications that need the same model contract as Tigrbl.

**Who is tigrbl_model for?**

Tigrbl maintainers, extension authors, and application developers who need validated models and portable serialization.

**Where does tigrbl_model fit?**

It is a foundational package under `pkgs/002_model`, below Tigrbl packages that consume models, validation, and JSON Schema.

**How does tigrbl_model work?**

Type annotations and `Field` metadata are compiled into an internal field graph. The graph drives validation, dumping, JSON Schema, and the JSON, YAML, and TOML mixins.

**Install**

```bash
uv add tigrbl-model
```

```bash
pip install tigrbl-model
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | `tigrbl-model` |
| Repository path | `pkgs/002_model/tigrbl_model` |
| Python import root | `tigrbl_model` |
| Console scripts | none |
| Public mixins | `JsonMixin`, `YamlMixin`, `TomlMixin`, `SerdeMixin` |
| Runtime Pydantic dependency | none |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_model` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_model` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/002_model/tigrbl_model/NOTICE) for attribution.
<!-- readme-standards:end notices -->
