# tigrbl-equivalence-contracts

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-equivalence-contracts</strong></p>
<p align="center">Local runtime demonstrations for certifiable Tigrbl equivalence claims.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-equivalence-contracts/"><img alt="pypi: tigrbl-equivalence-contracts unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-equivalence-contracts%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml"><img alt="Source version: 0.0.0+local" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.0.0%2Blocal&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml"><img alt="Layer: 96_examples" src="https://img.shields.io/static/v1?label=Layer&amp;message=96_examples&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-equivalence-contracts/"><img alt="pypi downloads: tigrbl-equivalence-contracts: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-equivalence-contracts%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/README.md"><img alt="README hits: tigrbl-equivalence-contracts" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/96_examples/equivalence_contracts/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

This local uv project contains runtime code and tests for assertable
equivalence demonstrations. It is not a PyPI package.

Run from the repository root:

```powershell
python tools/ci/validate_equivalence_runtime_contracts.py
```

Or run the local uv project directly:

```powershell
uv run --project pkgs/96_examples/equivalence_contracts --group dev python -m pytest -q pkgs/96_examples/equivalence_contracts/tests
```

Or run the tests with an already prepared environment:

```powershell
python -m pytest -q pkgs/96_examples/equivalence_contracts/tests
```

### Why This Package

Use this project for local runtime demonstrations for certifiable Tigrbl equivalence claims.

### When to Use

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

### Features

- `FrameworkImplementation`: One framework entry in an equivalence row.
- `CertificationResult`: The evidence produced after evaluating one equivalence row.
- `CertifiableEquivalence`: A row in the technical-marketing equivalence matrix.
- `Base`: declared in src/tigrbl_equivalence_contracts/equivalences/event_stream_table/fastapi_impl.py
- `WidgetRow`: declared in src/tigrbl_equivalence_contracts/equivalences/event_stream_table/fastapi_impl.py
- `WidgetOut`: declared in src/tigrbl_equivalence_contracts/equivalences/event_stream_table/fastapi_impl.py
- `Base`: declared in src/tigrbl_equivalence_contracts/equivalences/event_stream_table/flask_impl.py
- `WidgetRow`: declared in src/tigrbl_equivalence_contracts/equivalences/event_stream_table/flask_impl.py

### Non-Goals

`tigrbl-equivalence-contracts` owns local runtime demonstrations for certifiable Tigrbl equivalence claims. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml) declares runtime dependencies including `flask`, `flask-sock`, `fastapi`, `tigrbl-core`, `tigrbl`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`tigrbl-equivalence-contracts` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`tigrbl-equivalence-contracts` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`tigrbl-equivalence-contracts` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/tigrbl-equivalence-contracts
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/docs/readme/quick_start.py).

```python
import tigrbl_equivalence_contracts
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-equivalence-contracts` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/docs/readme/usage.py).

```python
import tigrbl_equivalence_contracts
```
<!-- readme-standards:end example.usage -->

The walkthrough above is retained. The entry surface can be loaded with:

### Configuration

Configure `tigrbl-equivalence-contracts` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/src/tigrbl_equivalence_contracts/contracts.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-equivalence-contracts` source raises `AssertionError`, `HTTPException`, `KeyError`, `RuntimeError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-equivalence-contracts` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `CERTIFIABLE_EQUIVALENCES`, `CertifiableEquivalence`, `CertificationResult`, `certify_all`, `equivalence_by_id`, `matrix_rows`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

Local runtime demonstrations for certifiable Tigrbl equivalence claims.

### Public API and Import Surfaces

Contract declarations and Tigrbl, FastAPI, and Flask comparison implementations. See the project source and existing examples above for supported call signatures.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-equivalence-contracts` are `flask`, `flask-sock`, `fastapi`, `tigrbl-core`, `tigrbl`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/src/tigrbl_equivalence_contracts/contracts.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl-equivalence-contracts` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl-equivalence-contracts`, use the source-declared public interfaces (`CERTIFIABLE_EQUIVALENCES`, `CertifiableEquivalence`, `CertificationResult`, `certify_all`, `equivalence_by_id`, `matrix_rows`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-equivalence-contracts` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-equivalence-contracts`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/src/tigrbl_equivalence_contracts/contracts.py). The `tigrbl-equivalence-contracts` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-equivalence-contracts` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-equivalence-contracts` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_certifiable_equivalences.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/tests/test_certifiable_equivalences.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/src/tigrbl_equivalence_contracts/contracts.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-equivalence-contracts` provides local runtime demonstrations for certifiable Tigrbl equivalence claims; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-equivalence-contracts`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/src/tigrbl_equivalence_contracts/contracts.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-equivalence-contracts` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/equivalence_contracts)

### Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-equivalence-contracts](https://pypi.org/project/tigrbl-equivalence-contracts/)
<!-- readme-standards:end project-links -->

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-equivalence-contracts`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/96_examples/equivalence_contracts` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-equivalence-contracts?**

Local runtime demonstrations for certifiable Tigrbl equivalence claims.

**When should I install tigrbl-equivalence-contracts?**

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

**Who is tigrbl-equivalence-contracts for?**

Tigrbl maintainers and application developers working with this project’s APIs.

**Where does tigrbl-equivalence-contracts fit?**

Source: `pkgs/96_examples/equivalence_contracts` in the Tigrbl workspace.

**How does tigrbl-equivalence-contracts work?**

Contract declarations and Tigrbl, FastAPI, and Flask comparison implementations. The examples and implementation above describe the configuration and execution flow.

**Install**

From the repository root:

```console
uv sync --project pkgs/96_examples/equivalence_contracts
```

**Surface Coverage**

| Surface | Value |
| --- | --- |
| Project | `tigrbl-equivalence-contracts` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `tigrbl_equivalence_contracts` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

**Workspace documentation**

This README is the package-local distribution entry point. See [workspace documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md), and [SSOT registry](../../../.ssot/registry.json).

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-equivalence-contracts` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-equivalence-contracts` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/LICENSE).
<!-- readme-standards:end license -->

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/96_examples/equivalence_contracts/NOTICE) for attribution.
<!-- readme-standards:end notices -->
