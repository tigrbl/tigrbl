# tigrbl-kernel

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-kernel</strong></p>
<p align="center">Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-kernel/"><img alt="pypi: tigrbl-kernel" src="https://img.shields.io/pypi/v/tigrbl-kernel?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml"><img alt="Layer: 045_kernel" src="https://img.shields.io/static/v1?label=Layer&amp;message=045_kernel&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-kernel/"><img alt="Monthly PyPI downloads: tigrbl-kernel" src="https://img.shields.io/pypi/dm/tigrbl-kernel?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/README.md"><img alt="README hits: tigrbl-kernel" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/045_kernel/tigrbl_kernel/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-kernel`: Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-kernel` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `ContractClassificationProjection`: declared in tigrbl_kernel/contract_classification.py
- `Kernel`: declared in tigrbl_kernel/core.py
- `EquivalenceCase`: declared in tigrbl_kernel/cross_transport.py
- `Label`: declared in tigrbl_kernel/labels.py
- `SchemaIn`: declared in tigrbl_kernel/models.py
- `SchemaOut`: declared in tigrbl_kernel/models.py
- `SchemaStored`: declared in tigrbl_kernel/models.py
- `OpView`: declared in tigrbl_kernel/models.py

### Non-Goals

`tigrbl-kernel` owns kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml) declares runtime dependencies including `tigrbl-typing`, `tigrbl-atoms`, `tigrbl-core`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-kernel
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-kernel
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-kernel
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_kernel")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-kernel` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_kernel")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-kernel
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-kernel"))
PY
```

**Import the package boundary**


**Import a public symbol**

```python
from tigrbl_kernel import BatchOpPlan

print(BatchOpPlan)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-kernel
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tigrbl_kernel/events.py) references configuration keys `HANDLER`, `POST_RESPONSE`, `PRE_TX_BEGIN`, `START_TX`. Consult the constructor or function signature before supplying them; a referenced key is not necessarily a global environment variable.

### Error Handling

The inspected `tigrbl-kernel` source raises `AtomFailure`, `AttributeError`, `IndexError`, `KeyError`, `RuntimeError`, `TypeError`, `ValueError`, `_unsupported`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

- Compile plans from explicit specs and bindings; do not guess transport behavior from URL strings alone.
- Keep protocol support checks fail-closed and close to planning.
- Preserve separate event rows for request, stream, message, session, and datagram families.
- Add tests at the kernel layer when changing hook order, labels, phase rows, protocol legality, or capability masks.
- Use measurement views for plan review instead of parsing private object internals.
- Keep runtime side effects out of kernel code; the kernel should plan, classify, and label, not perform IO.

---

## Package Boundary

### What It Owns

`tigrbl-kernel` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_kernel`: _build, _compile, atoms, cache, callbacks, contract_classification, core, eventkey, eventkey_hooks, events, helpers, hook_types

Package catalog:
- `tigrbl_kernel/core.py`, `tigrbl_kernel/_build.py`, `tigrbl_kernel/_compile.py`, `tigrbl_kernel/models.py`, `tigrbl_kernel/types.py`, and `tigrbl_kernel/payload.py`: kernel objects, operation views, packed plans, build/compile helpers, and payload contracts.
- `tigrbl_kernel/ordering.py`, `tigrbl_kernel/labels.py`, `tigrbl_kernel/hook_types.py`, `tigrbl_kernel/callbacks.py`, and `tigrbl_kernel/eventkey_hooks.py`: hook ordering, diagnostic labels, callback shape, and event-key-aware hook plumbing.
- `tigrbl_kernel/cache.py`, `tigrbl_kernel/trace.py`, and `tigrbl_kernel/measure.py`: cached plans, execution trace support, and measurement views.
- `tigrbl_kernel/atoms.py`, `tigrbl_kernel/transport_atoms.py`, and `tigrbl_kernel/transaction_units.py`: atom references and transaction/transport plan units.
- `tigrbl_kernel/protocol_bindings.py`, `tigrbl_kernel/protocol_phase_tree.py`, `tigrbl_kernel/protocol_chains/`, `tigrbl_kernel/protocol_completion.py`, `tigrbl_kernel/protocol_fusion.py`, and `tigrbl_kernel/protocol_legality_matrix.py`: transport-specific plan compilation, phase tree construction, chain definitions, completion semantics, fusion, and legality checks.
- `tigrbl_kernel/eventkey.py`, `tigrbl_kernel/events.py`, `tigrbl_kernel/transport_events.py`, `tigrbl_kernel/webtransport_events.py`, `tigrbl_kernel/subevent_taxonomy.py`, and `tigrbl_kernel/subevent_handlers.py`: event-key construction, subevent taxonomy, and protocol subevent handler mapping.
- `tigrbl_kernel/opchannel_capabilities.py`, `tigrbl_kernel/loop_modes.py`, `tigrbl_kernel/loop_regions.py`, `tigrbl_kernel/segment_fusion.py`, and `tigrbl_kernel/contract_classification.py`: channel capability checks, loop planning, segment grouping, and contract classification.

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-kernel`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_kernel`.
- Public symbols: `BatchOpPlan`, `Kernel`, `OpView`, `PackedKernel`, `SchemaIn`, `SchemaOut`, `build_kernel_plan`, `build_packed_kernel`, `build_packed_kernel_measurement_view`.
- Workspace dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/).
- External runtime dependencies: none declared.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-kernel` are `tigrbl-typing`, `tigrbl-atoms`, `tigrbl-core`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tigrbl_kernel/events.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-runtime`, `tigrbl`, `tigrbl-transport-surface-matrix-demo`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-kernel`, use the source-declared public interfaces (`BatchOpPlan`, `Kernel`, `OpView`, `PackedKernel`, `SchemaIn`, `SchemaOut`, `SchemaStored`, `build_kernel_plan`, `build_packed_kernel`, `build_packed_kernel_measurement_view`, `build_phase_chains`, `get_cached_specs`, `load_packed_kernel_hot_block`, `load_packed_kernel_hot_sections`, `measure_packed_kernel`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-kernel` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-kernel`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tigrbl_kernel/events.py). The `tigrbl-kernel` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-kernel` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-kernel` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_atoms.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tests/test_atoms.py)
- [tests/test_batch_plan_compilation.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tests/test_batch_plan_compilation.py)
- [tests/test_batch_policy_compilation.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tests/test_batch_policy_compilation.py)
- [tests/test_compile_opview_from_specs.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tests/test_compile_opview_from_specs.py)
- [tests/test_compile_plan.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tests/test_compile_plan.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/210_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tigrbl_kernel/events.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-kernel` provides kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-kernel`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/tigrbl_kernel/events.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-kernel` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

---

## Documentation and Related Packages

### More Documentation

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [Next steps](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/NEXT_STEPS.md)
- [Documentation pointers](https://github.com/tigrbl/tigrbl/blob/master/docs/governance/DOC_POINTERS.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

### Related Packages

- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/045_kernel/tigrbl_kernel)
- [pypi: tigrbl-kernel](https://pypi.org/project/tigrbl-kernel/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/045_kernel/tigrbl_kernel](https://github.com/tigrbl/tigrbl/tree/master/pkgs/045_kernel/tigrbl_kernel).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-kernel`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/045_kernel/tigrbl_kernel` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-kernel?**

Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.

**When should I install tigrbl-kernel?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-kernel for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-kernel fit?**

`tigrbl-kernel` lives at `pkgs/045_kernel/tigrbl_kernel` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-kernel work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

**Install**

```bash
uv add tigrbl-kernel
```

```bash
pip install tigrbl-kernel
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/) |
| Repository path | [`pkgs/045_kernel/tigrbl_kernel`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/045_kernel/tigrbl_kernel) |
| Python import root | `tigrbl_kernel` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Kernel Semantics**

The kernel turns specs, operation inventories, hooks, atoms, and protocol bindings into executable plans. It does not own app authoring syntax, persistence engines, or concrete ASGI classes. Its job is to compile the behavior that runtime-owned routing will execute.

The basic flow is:

```text
specs + model metadata + bindings + hooks
-> operation views
-> ordered phase plan
-> packed kernel
-> runtime execution and diagnostics
```

`Kernel` and `PackedKernel` are the planning surfaces; `OpView` is the operation-level view of schemas, handlers, hooks, bindings, and labels. `build_kernel_plan(...)` and `build_packed_kernel(...)` are useful for tests and framework packages that need to verify the compiled plan without driving a full ASGI request.

**Protocol Planning**

Protocol planning keeps binding kind, family, framing, exchange, lane, subevent rows, and atom anchors separate. The current planner handles:

| Binding kind | Runtime family | Default framing | Plan shape |
|---|---|---|---|
| `http.rest` / `https.rest` | request | JSON | request received, handler invoke, response emit. |
| `http.jsonrpc` / `https.jsonrpc` | request | JSON-RPC | framing decode, dispatch, handler invoke, framing encode. |
| `http.stream` / `https.stream` | stream | stream | handler invoke, transport emit, stream close. |
| `http.sse` / `https.sse` | stream | SSE | encode event, emit event, close stream. |
| `ws` / `wss` / `websocket` | message | text or negotiated JSON-RPC | accept, decode, dispatch, handler, emit/close. |
| `webtransport` | session, stream, or datagram | no top-level app framing | lane-specific session, stream, or datagram rows with lane-local framing validation. |

Unsupported or ambiguous bindings raise planning errors. For example, WebSocket bindings do not accept HTTP methods, HTTP JSON-RPC requires an RPC method, WebTransport request/response exchange is unsupported, and WebTransport app framing must be declared on the relevant control stream, stream, or datagram lane.

**Hook Ordering and Labels**

The kernel orders security dependencies, dependencies, system hooks, user hooks, atoms, and handlers into phase plans. Labels are part of the diagnostics contract:

```text
PRE_HANDLER:secdep:myapp.auth.require_user
PRE_HANDLER:dep:myapp.context.load_tenant
HANDLER:hook:sys:handler:create@HANDLER
EGRESS_SHAPE:atom:wire:dump
```

Use labels to debug and test ordering. Do not use them as application APIs; use specs, decorators, dependencies, and hooks for configuration.

**Diagnostics and Traceability**

Kernel plans feed `/system/kernelz` in concrete applications. Trace and measurement helpers make it possible to assert plan shape, count phase work, and inspect compiled execution without relying on a live server. This is especially important for transport work, where a route can look correct while the protocol chain is missing required event rows or capability masks.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-kernel` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-kernel` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/045_kernel/tigrbl_kernel/NOTICE) for attribution.
<!-- readme-standards:end notices -->
