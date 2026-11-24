# tigrbl-runtime

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-runtime</strong></p>
<p align="center">Execution bridge for compiled Tigrbl kernel plans and narrow runtime context/carrier compatibility.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-runtime/"><img alt="pypi: tigrbl-runtime" src="https://img.shields.io/pypi/v/tigrbl-runtime?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml"><img alt="Source version: 0.4.6.dev3" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev3&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml"><img alt="Layer: 50_runtime" src="https://img.shields.io/static/v1?label=Layer&amp;message=50_runtime&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-runtime/"><img alt="Monthly PyPI downloads: tigrbl-runtime" src="https://img.shields.io/pypi/dm/tigrbl-runtime?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/README.md"><img alt="README hits: tigrbl-runtime" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/50_runtime/tigrbl_runtime/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-runtime`: Execution bridge for compiled Tigrbl kernel plans and narrow runtime context/carrier compatibility.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-runtime` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `OpChannelCapabilityError`: declared in tigrbl_runtime/channel/capabilities.py
- `RuntimeWebSocketRoute`: declared in tigrbl_runtime/channel/websocket.py
- `RuntimeWebSocket`: declared in tigrbl_runtime/channel/websocket.py
- `ExecutorBase`: Contract for runtime executors.
- `Request`: declared in tigrbl_runtime/executors/ctx/context.py
- `HotCtx`: declared in tigrbl_runtime/executors/ctx/hot_state.py
- `NumbaPackedPlanExecutor`: Executes packed plans and prioritizes numba-compiled route dispatch.
- `PackedPlanExecutor`: Executes packed kernel plans via kernel-attached packed execution hooks.

### Non-Goals

`tigrbl-runtime` owns execution bridge for compiled Tigrbl kernel plans and narrow runtime context/carrier compatibility. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml) declares runtime dependencies including `tigrbl-typing`, `tigrbl-kernel`, `tigrbl-atoms`, `tigrbl-base`, `tigrbl-core`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-runtime
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-runtime
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-runtime
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_runtime")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-runtime` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_runtime")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-runtime
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-runtime"))
PY
```

**Import the package boundary**


**Import a public symbol**

```python
from tigrbl_runtime import Runtime

print(Runtime)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-runtime
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tigrbl_runtime/__init__.py) references configuration keys `TX_ROLLBACK`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `tigrbl-runtime` source raises `AttributeError`, `HTTPException`, `KeyError`, `OpChannelCapabilityError`, `RuntimeError`, `SemanticReactionError`, `SystemStepError`, `TypeError`, `ValueError`, `create_standardized_error`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-runtime` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `Any`, `annotations`, `import_module`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-runtime` owns the compiled-plan execution boundary. It should be installed when you need the narrow bridge that runs already-planned Tigrbl work without assuming the full facade is present.

Implementation orientation:
- `tigrbl_runtime`: compiled plan execution, runtime context compatibility, and declared carrier lifecycle bridges

Runtime authoring BCP:
- Do use this package for executing compiled kernel plans and maintaining runtime context/carrier compatibility.
- Do keep execution aligned with compiled plans.
- Do not add route matching semantics, protocol fallback policy, JSON-RPC/REST envelope policy, response rendering, chunk emission semantics, operation behavior, or new executor families.
- Do not make application route handlers, FastAPI/Starlette objects, direct SQLAlchemy session calls, or ad-hoc engine construction the runtime contract.
- Do not bypass kernel plans or lifecycle phases when adding REST, JSON-RPC, stream, SSE, WebSocket, or WebTransport behavior.
- Avoid hiding behavior in runtime wrappers that diagnostics and compiled plans cannot inspect.

This README is the package-local distribution entry point for `tigrbl-runtime`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_runtime`.
- Public symbols: `Runtime`, `RuntimeBase`.
- Workspace dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/), [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/).
- Optional Numba dependency (`numba` extra): `numba>=0.61.2`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-runtime` are `tigrbl-typing`, `tigrbl-kernel`, `tigrbl-atoms`, `tigrbl-base`, `tigrbl-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tigrbl_runtime/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-concrete`, `tigrbl`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-runtime`, use the source-declared public interfaces (`Any`, `annotations`, `import_module`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-runtime` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-runtime`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tigrbl_runtime/__init__.py). The `tigrbl-runtime` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-runtime` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-runtime` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_channel_lifecycle_reactions_t012.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tests/test_channel_lifecycle_reactions_t012.py)
- [tests/test_channel_runtime_surface.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tests/test_channel_runtime_surface.py)
- [tests/test_ctx_promote_compat.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tests/test_ctx_promote_compat.py)
- [tests/test_invoke_entrypoint_modes.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tests/test_invoke_entrypoint_modes.py)
- [tests/test_invoke_phase_db.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tests/test_invoke_phase_db.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tigrbl_runtime/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-runtime` provides execution bridge for compiled Tigrbl kernel plans and narrow runtime context/carrier compatibility; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-runtime`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/tigrbl_runtime/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-runtime` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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

- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/50_runtime/tigrbl_runtime)
- [pypi: tigrbl-runtime](https://pypi.org/project/tigrbl-runtime/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/50_runtime/tigrbl_runtime](https://github.com/tigrbl/tigrbl/tree/master/pkgs/50_runtime/tigrbl_runtime).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-runtime`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/50_runtime/tigrbl_runtime` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-runtime?**

`tigrbl-runtime` executes compiled Tigrbl kernel plans and preserves the narrow runtime context/carrier bridge needed to run those plans. Route selection, protocol fallback policy, response shaping, transport envelopes, and operation semantics are owned by kernel, atoms, and ops packages.

**When should I install tigrbl-runtime?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-runtime for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-runtime fit?**

`tigrbl-runtime` lives at `pkgs/50_runtime/tigrbl_runtime` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-runtime work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-runtime
```

```bash
pip install tigrbl-runtime
```

The base install uses the Python dispatcher. Install `tigrbl-runtime[numba]` to use Numba-compiled route dispatch with the `numba_packed` executor.

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) |
| Repository path | [`pkgs/50_runtime/tigrbl_runtime`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/50_runtime/tigrbl_runtime) |
| Python import root | `tigrbl_runtime` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | `numba` |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10 | 3.11 | 3.12 | 3.13 | 3.14` |

**Lowering integration**

`lowering_services` lazily exposes canonical kernel operation-view compilation and WebSocket JSON-RPC session construction to concrete integration code. It preserves the kernel function objects and keeps kernel imports out of concrete authoring modules.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-runtime` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-runtime` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/50_runtime/tigrbl_runtime/NOTICE) for attribution.
<!-- readme-standards:end notices -->
