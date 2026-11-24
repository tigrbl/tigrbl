# tigrbl_tests

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl_tests</strong></p>
<p align="center">Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_tests/"><img alt="pypi: tigrbl_tests" src="https://img.shields.io/pypi/v/tigrbl_tests?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml"><img alt="Layer: 97_tests" src="https://img.shields.io/static/v1?label=Layer&amp;message=97_tests&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl_tests/"><img alt="Monthly PyPI downloads: tigrbl_tests" src="https://img.shields.io/pypi/dm/tigrbl_tests?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/README.md"><img alt="README hits: tigrbl_tests" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/97_tests/tigrbl_tests/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl_tests`: Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.

### Why This Package

Use it when downstream packages need the same Tigrbl fixtures, conformance helpers, and regression assertions used by the workspace.

### When to Use

Choose `tigrbl_tests` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `FactoryCandidate`: declared in tigrbl_tests/factory_conformance/discovery.py
- `FactoryAlias`: declared in tigrbl_tests/factory_conformance/manifest.py
- `FactorySurface`: declared in tigrbl_tests/factory_conformance/manifest.py
- `FactoryManifest`: declared in tigrbl_tests/factory_conformance/manifest.py

### Non-Goals

`tigrbl_tests` owns reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml) declares runtime dependencies including `tigrbl`, `tigrbl-examples`, `tigrbl-client`, `psycopg2-binary`, `asyncpg`, `pytest`, `pytest-asyncio`, `pytest-xdist`, `pytest-json-report`, `python-dotenv`, `requests`, `flake8`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl_tests
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl_tests
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl_tests
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/docs/readme/quick_start.py).

```python
import tigrbl_tests

print(tigrbl_tests.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl_tests` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/docs/readme/usage.py).

```python
import tigrbl_tests

print(tigrbl_tests.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl_tests
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl_tests"))
PY
```

**Run packaged Tigrbl tests**

```bash
uv run pytest pkgs/97_tests/tigrbl_tests/tests -q
python -m pytest --pyargs tigrbl_tests
```

**Import reusable test helpers**


**Use it in downstream CI**

```bash
pip install tigrbl-tests pytest
pytest -q
```

### Configuration

Configure `tigrbl_tests` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tigrbl_tests/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl_tests` source raises `AssertionError`, `ValueError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl_tests` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `FactoryCandidate`, `FactoryAlias`, `FactorySurface`, `FactoryManifest`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl_tests` owns the `test support package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `benchmarks`: comparative_benchmark_verification, open_loop_load_patterns, run_hot_path_perf_suite, tigrbl_fastapi_surface_matrix_benchmark, tigrbl_kernel_plan_benchmark, tigrbl_request_response_benchmark, tigrbl_sse_perf_suite, tigrbl_streaming_perf_suite, tigrbl_websocket_perf_suite, tigrbl_webtransport_perf_suite
- `tigrbl_tests`: tests/
- `v4`: tests/

This README is the package-local distribution entry point for `tigrbl_tests`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `benchmarks`, `tigrbl_tests`, `triage_tests`, `v4`.
- Public symbols: public surface is module-oriented; import the package boundary and inspect submodules as needed.
- Workspace dependencies: [`tigrbl`](https://pypi.org/project/tigrbl/), [`tigrbl-examples`](https://pypi.org/project/tigrbl-examples/), [`tigrbl_client`](https://pypi.org/project/tigrbl_client/).
- External runtime dependencies: `psycopg2-binary>=2.9.9`, `asyncpg>=0.30.0`, `pytest>=8.0`, `pytest-asyncio>=0.24.0`, `pytest-xdist>=3.6.1`, `pytest-json-report>=1.5.0`, `python-dotenv`, `requests>=2.32.3`, `flake8>=7.0`, `pytest-timeout>=2.3.1`, `ruff>=0.9.9`, `pytest-benchmark>=4.0.0`, `jinja2>=3.1.0`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl_tests` are `tigrbl`, `tigrbl-examples`, `tigrbl-client`, `psycopg2-binary`, `asyncpg`, `pytest`, `pytest-asyncio`, `pytest-xdist`, `pytest-json-report`, `python-dotenv`, `requests`, `flake8`, `pytest-timeout`, `ruff`, `pytest-benchmark`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tigrbl_tests/__init__.py).

### Protocol Consumers

No direct package-manifest dependency on `tigrbl_tests` was found in the audited three-repository inventory. External consumers may still use its documented imports or commands.

### Extensions

For `tigrbl_tests`, use the source-declared public interfaces (`FactoryCandidate`, `FactoryAlias`, `FactorySurface`, `FactoryManifest`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl_tests` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl_tests`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tigrbl_tests/__init__.py). The `tigrbl_tests` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl_tests` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl_tests` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_secdeps_execute_in_pre_tx.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tests/test_secdeps_execute_in_pre_tx.py)
- [tests/architecture/test_import_graph_audit.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tests/architecture/test_import_graph_audit.py)
- [tests/architecture/test_no_bindings_imports.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tests/architecture/test_no_bindings_imports.py)
- [tests/architecture/test_operation_resolution_parity.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tests/architecture/test_operation_resolution_parity.py)
- [tests/architecture/test_route_to_pathspec_migration.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tests/architecture/test_route_to_pathspec_migration.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tigrbl_tests/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl_tests` provides reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl_tests`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/tigrbl_tests/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl_tests` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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
- [`tigrbl-examples`](https://pypi.org/project/tigrbl-examples/)
- [`tigrbl_client`](https://pypi.org/project/tigrbl_client/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/97_tests/tigrbl_tests)
- [pypi: tigrbl_tests](https://pypi.org/project/tigrbl_tests/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/97_tests/tigrbl_tests](https://github.com/tigrbl/tigrbl/tree/master/pkgs/97_tests/tigrbl_tests).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl_tests`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/97_tests/tigrbl_tests` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl_tests?**

Reusable Tigrbl pytest fixtures, conformance assertions, integration helpers, and package test utilities.

**When should I install tigrbl_tests?**

Install it in CI, package-local validation, transport integration tests, and compatibility checks.

**Who is tigrbl_tests for?**

Maintainers, extension authors, and integration teams validating Tigrbl-compatible packages.

**Where does tigrbl_tests fit?**

`tigrbl_tests` lives at `pkgs/97_tests/tigrbl_tests` and serves reusable test, conformance, and integration support for Tigrbl packages.

**How does tigrbl_tests work?**

It packages reusable pytest assets and helper modules that exercise public Tigrbl behavior instead of relying on private workspace state.

**Install**

```bash
uv add tigrbl_tests
```

```bash
pip install tigrbl_tests
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl_tests`](https://pypi.org/project/tigrbl_tests/) |
| Repository path | [`pkgs/97_tests/tigrbl_tests`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/97_tests/tigrbl_tests) |
| Python import root | `benchmarks`, `tigrbl_tests`, `triage_tests`, `v4` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl_tests` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl_tests` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/97_tests/tigrbl_tests/NOTICE) for attribution.
<!-- readme-standards:end notices -->
