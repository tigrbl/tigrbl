# tigrbl-atoms

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-atoms</strong></p>
<p align="center">Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-atoms/"><img alt="pypi: tigrbl-atoms" src="https://img.shields.io/pypi/v/tigrbl-atoms?labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml"><img alt="Source version: 0.4.6.dev2" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.4.6.dev2&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml"><img alt="Layer: 40_atoms" src="https://img.shields.io/static/v1?label=Layer&amp;message=40_atoms&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-atoms/"><img alt="Monthly PyPI downloads: tigrbl-atoms" src="https://img.shields.io/pypi/dm/tigrbl-atoms?labelColor=1E293B&amp;color=0E7490"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/README.md"><img alt="README hits: tigrbl-atoms" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/40_atoms/tigrbl_atoms/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/docs/readme/test_examples.py"><img alt="Tests: example source" src="https://img.shields.io/static/v1?label=Tests&amp;message=example%20source&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

`tigrbl-atoms`: Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.

### Why This Package

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

### When to Use

Choose `tigrbl-atoms` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

### Features

- `UploadedFile`: declared in tigrbl_atoms/_request.py
- `Request`: declared in tigrbl_atoms/_request.py
- `BatchPolicy`: declared in tigrbl_atoms/atoms/batch/_types.py
- `BatchAdmission`: declared in tigrbl_atoms/atoms/batch/_types.py
- `BatchGroup`: declared in tigrbl_atoms/atoms/batch/_types.py
- `AtomImpl`: declared in tigrbl_atoms/atoms/batch/abort_group.py
- `AtomImpl`: declared in tigrbl_atoms/atoms/batch/admit.py
- `AtomImpl`: declared in tigrbl_atoms/atoms/batch/await_seal.py

### Non-Goals

`tigrbl-atoms` owns runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra. Its imports do not by themselves configure credentials, deploy a service, or certify the behavior of its consumers. Dependencies and neighboring packages retain their own documented responsibilities.

---

## Getting Started

### Prerequisites

Python `>=3.10,<3.15` is required. The [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml) declares runtime dependencies including `tigrbl-ops-oltp`, `tigrbl-ops-olap`, `tigrbl-ops-realtime`, `tigrbl-ops-webtransport`, `tigrbl-core`, `tigrbl-typing`, `jinja2`, `sqlalchemy`, `typing-extensions`. Read the example’s inputs and service requirements before execution.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
```bash
uv add tigrbl-atoms
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
```bash
python -m pip install tigrbl-atoms
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
```bash
poetry add tigrbl-atoms
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/docs/readme/quick_start.py).

```python
import importlib

module = importlib.import_module("tigrbl_atoms")
print(module.__name__)
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The example demonstrates the documented `tigrbl-atoms` source boundary or workflow. Complete its required configuration first. README CI checks the maintained source’s syntax and declarations; it does not claim that external services or the application workflow were exercised.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/docs/readme/usage.py).

```python
import importlib

module = importlib.import_module("tigrbl_atoms")
print(module.__name__)
```
<!-- readme-standards:end example.usage -->

**Verify the installed package**

```bash
python -m pip show tigrbl-atoms
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-atoms"))
PY
```

**Import the package boundary**


**Import a public symbol**

```python
from tigrbl_atoms import EGRESS_PHASES

print(EGRESS_PHASES)
```

**Use with the facade when building applications**

```bash
uv add tigrbl tigrbl-atoms
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

### Configuration

Configure `tigrbl-atoms` through the APIs in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tigrbl_atoms/__init__.py); its [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml) describes installation requirements, not an implicit service configuration. No additional package-global configuration contract is inferred from dependencies.

### Error Handling

The inspected `tigrbl-atoms` source raises `AssertionError`, `AttributeError`, `BufferError`, `CallbackRuntimeError`, `FileNotFoundError`, `HTTPException`, `KeyError`, `LookupError`, `NotImplementedError`, `PermissionError`. Handle these at the calling boundary and consult the implementation for the triggering conditions.

### Best Practices

Use the explicit `tigrbl-atoms` imports documented below and keep collaborator configuration with the caller. Run the package’s relevant tests after changing `EGRESS_PHASES`, `EdgeTarget`, `ErrorCtx`, `HANDLER_PHASES`, `HookPhase`, `HookPhases`, `HookPredicate`, `INGRESS_PHASES`, `PHASE_SEQUENCE`, `PhaseTreeEdge`, `PhaseTreeNode`, `StepFn`, `TypedErr`, `VALID_HOOK_PHASES`, `build_error_ctx`; an import or successful installation alone does not establish its runtime guarantees.

---

## Package Boundary

### What It Owns

`tigrbl-atoms` owns the `foundational framework package` boundary. It should be installed when you need this package's focused responsibility without assuming every other Tigrbl workspace package is present.

Implementation orientation:
- `tigrbl_atoms`: _ctx, _opview_helpers, _request, algebra, atoms/, events, fallback, phases, protocol_runtime, runtime_callbacks, runtime_channel, runtime_transactions

Package catalog:
- `phases.py` and `stages.py`: lifecycle phase names, aliases, stage transitions, transaction flags, and error-phase metadata.
- `_ctx.py`, `_request.py`, `types.py`, and `events.py`: typed context, request, event, and callable contracts shared by kernel/runtime code.
- `algebra.py`: composable pipeline helpers for sequencing runtime work.
- `atoms/ingress`: context initialization, transport extraction, and input preparation.
- `atoms/dispatch`: binding matching, binding parsing, operation resolution, and input normalization.
- `atoms/dep`: security dependency, general dependency, and parameter resolution units.
- `atoms/wire`: input schema construction, input validation, output construction, and dump/serialization units.
- `atoms/sys`: default system handlers for CRUD, bulk, analytics, realtime, transport, transaction, and persistence operations.
- `atoms/storage`, `atoms/out`, `atoms/response`, `atoms/egress`, and `atoms/err`: storage conversion, masking, response negotiation/rendering, transport egress, error shaping, and rollback.
- `atoms/batch`, `atoms/fanout`, `atoms/hot`, `atoms/intent`, and `atoms/transport`: batch scheduling, fanout shaping, hot slots, intent grouping, and transport sink/capture units.
- `protocol_runtime.py`, `runtime_channel.py`, `runtime_callbacks.py`, and `runtime_transactions.py`: helpers used by runtime-owned protocol execution.

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-atoms`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

### Public API and Import Surfaces

- Import roots: `tigrbl_atoms`.
- Public symbols: `EGRESS_PHASES`, `EdgeTarget`, `ErrorCtx`, `HANDLER_PHASES`, `HookPhase`, `HookPhases`, `HookPredicate`, `INGRESS_PHASES`, `PHASE_SEQUENCE`, `PhaseTreeEdge`, `PhaseTreeNode`, `StepFn`.
- Workspace dependencies: [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `jinja2>=3.1`, `sqlalchemy>=2.0`, `typing-extensions>=4.0`.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The direct installation dependencies of `tigrbl-atoms` are `tigrbl-ops-oltp`, `tigrbl-ops-olap`, `tigrbl-ops-realtime`, `tigrbl-ops-webtransport`, `tigrbl-core`, `tigrbl-typing`, `jinja2`, `sqlalchemy`, `typing-extensions`. These declarations do not imply automatic provider selection. Pass collaborators through the explicit constructors or call signatures in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tigrbl_atoms/__init__.py).

### Protocol Consumers

Direct consumers in this checkout’s package manifests include `tba-workspace`, `tigrbl-base`, `tigrbl-kernel`, `tigrbl-runtime`, `tigrbl-concrete`, `tigrbl`. These edges describe declared dependencies, not protocol-conformance evidence.

### Extensions

For `tigrbl-atoms`, use the source-declared public interfaces (`EGRESS_PHASES`, `EdgeTarget`, `ErrorCtx`, `HANDLER_PHASES`, `HookPhase`, `HookPhases`, `HookPredicate`, `INGRESS_PHASES`, `PHASE_SEQUENCE`, `PhaseTreeEdge`, `PhaseTreeNode`, `StepFn`, `TypedErr`, `VALID_HOOK_PHASES`, `build_error_ctx`) when composing or extending behavior. Its entry-point section below is authoritative for registered plugins; no additional extension loader is inferred from the package name.

---

## Operations and Readiness

### Operational Requirements

Operate `tigrbl-atoms` according to its actual entry points and collaborators. The dependency and Python requirements in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml) are prerequisites; deployment topology, credentials, and readiness remain the responsibility of the consuming application unless explicitly documented above.

### Health and Observability

This README does not establish a standalone health endpoint for `tigrbl-atoms`. Observe the concrete caller’s results, exceptions, and existing test reports. An application that embeds this package must define its own health and telemetry contract.

### Security and Resource Limits

Apply the input, credential, and resource constraints implemented in [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tigrbl_atoms/__init__.py). The `tigrbl-atoms` README gate is a documentation check, not a security review or a substitute for the implementation’s limits and caller authorization.

### Compatibility

This source version of `tigrbl-atoms` declares Python `>=3.10,<3.15`. Consult its dependency constraints before upgrading. Source-version and registry-version badges have separate meanings; this migration makes no additional platform or interoperability certification claim.

---

## Verification

### Tests

Run `python -m pytest docs/readme/test_examples.py` from the `tigrbl-atoms` package directory for the maintained example source checks (Python compilation and non-Python file presence). Existing package tests include:

- [tests/test_batch_atoms.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tests/test_batch_atoms.py)
- [tests/test_batch_execute_policy.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tests/test_batch_execute_policy.py)
- [tests/test_batch_fanout.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tests/test_batch_fanout.py)
- [tests/test_batch_prepare_execute.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tests/test_batch_prepare_execute.py)
- [tests/test_declared_dependency_imports.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tests/test_declared_dependency_imports.py)

The repository README gate also checks the required heading tree, metadata, managed fragments, and referenced files.

### Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

### Evidence

The [README standards CI](https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml) records mechanical documentation results for its tested commit. The [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tigrbl_atoms/__init__.py) and example sources support the package-boundary description; external runtime behavior requires its own test evidence.

---

## FAQ

### Why

**Why select this package?** `tigrbl-atoms` provides runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra; use its own API boundary rather than assuming neighboring packages are bundled or configured automatically.

### How

**How do I start?** Install or synchronize the environment under Getting Started, follow the maintained example for `tigrbl-atoms`, and consult [package source](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/tigrbl_atoms/__init__.py) for the exact types and signatures involved.

### When

**When should I validate an upgrade?** Recheck `tigrbl-atoms` whenever its source version, declared collaborators, configuration, or caller changes. Run relevant behavioral tests in addition to the README gate before promotion.

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

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

### Project Links

<!-- readme-standards:begin project-links -->
- [Discord](https://discord.gg/K4YTAPapjR)
- [Homepage](https://github.com/tigrbl/tigrbl)
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Organization](https://github.com/tigrbl)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/40_atoms/tigrbl_atoms)
- [pypi: tigrbl-atoms](https://pypi.org/project/tigrbl-atoms/)
<!-- readme-standards:end project-links -->

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/40_atoms/tigrbl_atoms](https://github.com/tigrbl/tigrbl/tree/master/pkgs/40_atoms/tigrbl_atoms).

---

## Contributing

### How to Contribute

Follow the [contribution guide](https://github.com/tigrbl/tigrbl/blob/master/CONTRIBUTING.md) and include a focused example or regression for changes to `tigrbl-atoms`. Keep package behavior, its documented boundary, and its tests aligned.

### Development Setup

Work from the `pkgs/40_atoms/tigrbl_atoms` checkout. Synchronize its declared development environment with uv, then run the relevant package tests and `python -m pytest docs/readme/test_examples.py`. The repository’s dedicated README job installs `readme-standards==0.1.3` without resolving unrelated runtime packages.

### Notes for Maintainers

**What is tigrbl-atoms?**

Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.

**When should I install tigrbl-atoms?**

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

**Who is tigrbl-atoms for?**

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

**Where does tigrbl-atoms fit?**

`tigrbl-atoms` lives at `pkgs/40_atoms/tigrbl_atoms` and serves a focused layer in the split Tigrbl framework.

**How does tigrbl-atoms work?**

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

Inbound materialization belongs to `wire.validate_in`, which uses the core schema
materializer and declared field types (or mapped storage types when no field type
is declared). Member identifiers are selector inputs even when the primary key
is not writable. Route selectors take precedence over payload identifiers and
invalid selectors raise 422 before persistence. Persistence atoms consume the
validated payload and path carriers, including bulk values; CRUD helpers do not
repeat type coercion. Selector operations currently use the full atom pipeline
because the compiled scalar input shortcut does not implement route alias and
selector precedence validation. CRUD operations retain their existing flush-only
transaction contract; the caller owns commit or rollback.

**Install**

```bash
uv add tigrbl-atoms
```

```bash
pip install tigrbl-atoms
```

**Surface Coverage**

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/) |
| Repository path | [`pkgs/40_atoms/tigrbl_atoms`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/40_atoms/tigrbl_atoms) |
| Python import root | `tigrbl_atoms` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

**Lifecycle Phases**

Atoms are organized around the runtime lifecycle:

| Group | Phases | Meaning |
|---|---|---|
| Ingress | `INGRESS_BEGIN`, `INGRESS_PARSE`, `INGRESS_DISPATCH` | Receive a transport unit, initialize context, parse input, and resolve the target binding/operation. |
| Transaction and handler | `PRE_TX_BEGIN`, `START_TX`, `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, `TX_COMMIT` | Prepare policy, open or attach transaction state, validate input, run handlers, post-process, and commit when Tigrbl owns the transaction. |
| Egress | `POST_COMMIT`, `EGRESS_SHAPE`, `EGRESS_FINALIZE`, `POST_RESPONSE` | Shape output, apply response rules, finalize transport output, and run after-response work. |
| Error | `ON_ERROR`, phase-specific `ON_*_ERROR`, `TX_ROLLBACK` | Classify errors, shape error responses, and roll back transaction-owned work. |

`END_TX`, `ON_END_TX_ERROR`, and `ON_ROLLBACK` are compatibility aliases for `TX_COMMIT`, `ON_TX_COMMIT_ERROR`, and `TX_ROLLBACK`. New docs and new atoms should use the current names.

**Atom Semantics**

An atom is a small, named runtime unit. It should do one thing, take context from the compiled plan, and leave the context in the expected next stage. Atoms are intentionally smaller than handlers:

- ingress atoms do not perform persistence;
- dispatch atoms do not execute business logic;
- wire atoms do not choose transport routes;
- storage atoms do not commit transactions;
- egress atoms do not reopen handler work;
- error atoms should be deterministic and avoid masking the original failure unless policy requires it.

This separation lets the kernel produce readable labels, lets diagnostics explain execution order, and lets runtime transports share behavior across REST, JSON-RPC, stream, SSE, WebSocket, WSS, and WebTransport surfaces.

**System Handler Catalog**

The `atoms/sys` package contains default handlers and transaction units used by operation packs and runtime plans. The catalog includes scalar CRUD handlers (`create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `clear`), bulk handlers, analytical handlers (`count`, `exists`, `aggregate`, `group_by`), realtime handlers (`publish`, `subscribe`, `tail`), stream/file handlers (`upload`, `download`, `append_chunk`, `checkpoint`), custom/no-op handlers, persistence helpers, and transaction helpers such as `start_tx`, `phase_db`, and `commit_tx`.

Use system handlers when implementing framework behavior. Application code should normally reach these through operations on a Tigrbl app or model rather than importing a handler atom directly.

**Transaction Discipline**

Transaction atoms and database guards exist so user hooks and system handlers do not silently commit or flush at the wrong phase. The broad rule is:

- before `START_TX`, do not assume a database transaction exists;
- from `START_TX` through `PRE_COMMIT`, in-transaction validation and handler work may proceed under guards;
- `TX_COMMIT` owns final commit when Tigrbl owns the transaction;
- `POST_COMMIT`, `EGRESS_*`, and `POST_RESPONSE` should not mutate transaction-owned state;
- `TX_ROLLBACK` performs rollback and cleanup for failures.

If you add or modify an atom, make its transaction expectations explicit in tests. Do not hide direct session commits inside validation, response, transport, or error atoms.

**Transport and Protocol Atoms**

Transport atoms model runtime units instead of broad protocol names. A WebSocket message, an SSE event, an HTTP stream chunk, and a WebTransport datagram are different units even when they carry similar payloads. Keep family, exchange, framing, lane, subevent, and handler intent separate.

Practical guidance:
- Use ingress/dispatch atoms to parse and resolve transport units.
- Use protocol/runtime helpers to carry channel metadata.
- Use response and egress atoms to render or emit units.
- Preserve fail-closed behavior for unsupported protocol/framing/lane combinations.

**Extension Guidance**

- Add atoms when the behavior is reusable, phase-specific, and independently testable.
- Keep application policy in hooks or dependencies, not in generic atoms.
- Keep atom names stable and descriptive; they show up in kernel diagnostics.
- Avoid broad atoms that parse, validate, execute, persist, and render at once.

---

## Governance

### Ownership and Decision Making

Changes to `tigrbl-atoms` follow the maintainer review process of [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl) and its contribution guide. Author attribution remains in the [manifest](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/pyproject.toml); this README does not assign new publishing or administrative authority.

### Standards and Policies

`tigrbl-atoms` follows the versioned [package-guide-v1 outline](https://github.com/groupsum/readme-standards/blob/master/docs/outline.md). All fixed headings, hierarchy, order, separators, and package-specific branding are checked by CI; reviewers assess the accuracy and usefulness of authored claims.

### Lifecycle and Migration

Source and published versions are identified separately in the branding badges above. This change standardizes documentation and adds a development-only gate; it does not publish a new runtime version or declare a previously unpublished package released. Preserve explicit deprecation and replacement instructions where present.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/LICENSE).
<!-- readme-standards:end license -->

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/NOTICE) for attribution.
<!-- readme-standards:end notices -->
