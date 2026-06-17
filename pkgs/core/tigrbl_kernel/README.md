<div align="center">
<h1>tigrbl-kernel</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.</strong></p>
<a href="https://pypi.org/project/tigrbl-kernel/"><img src="https://img.shields.io/pypi/v/tigrbl-kernel?label=PyPI" alt="PyPI version for tigrbl-kernel"/></a>
<a href="https://pypi.org/project/tigrbl-kernel/"><img src="https://static.pepy.tech/badge/tigrbl-kernel" alt="Downloads for tigrbl-kernel"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-kernel"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_kernel/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/core/tigrbl_kernel/README.md.svg?label=hits" alt="Repository hits for tigrbl-kernel README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-kernel"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-kernel"/></a>
</div>

## What is tigrbl-kernel?

Kernel orchestration for composing Tigrbl runtime plans, bindings, operation dispatch, and optimized ASGI execution.

## Why use tigrbl-kernel?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-kernel?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-kernel for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-kernel fit?

`tigrbl-kernel` lives at `pkgs/core/tigrbl_kernel` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-kernel work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/core/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## Install

```bash
uv add tigrbl-kernel
```

```bash
pip install tigrbl-kernel
```

## Surface Coverage

| Surface | Value |
|---|---|
| PyPI package | [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/) |
| Repository path | [`pkgs/core/tigrbl_kernel`](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_kernel) |
| Python import root | `tigrbl_kernel` |
| Console scripts | none declared |
| Entry points | none declared |
| Optional extras | none declared |
| Legal files | `LICENSE`, `NOTICE` |
| Supported Python | `3.10, 3.11, 3.12, 3.13, 3.14` |

## What It Owns

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
- `tigrbl_kernel/rust_plan.py`, `tigrbl_kernel/rust_compile.py`, and `tigrbl_kernel/rust_spec.py`: deprecated compatibility shims; kernel planning is Python-only.

## Public API and Import Surface

- Import roots: `tigrbl_kernel`.
- Public symbols: `BatchOpPlan`, `ExecutionBackend`, `Kernel`, `OpView`, `PackedKernel`, `SchemaIn`, `SchemaOut`, `build_kernel_plan`, `build_packed_kernel`, `build_packed_kernel_measurement_view`.
- Workspace dependencies: [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/), [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/).
- External runtime dependencies: none declared.

## Kernel Semantics

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

## Protocol Planning

Protocol planning keeps binding kind, family, framing, exchange, lane, subevent rows, and atom anchors separate. The current planner handles:

| Binding kind | Runtime family | Default framing | Plan shape |
|---|---|---|---|
| `http.rest` / `https.rest` | request | JSON | request received, handler invoke, response emit. |
| `http.jsonrpc` / `https.jsonrpc` | request | JSON-RPC | framing decode, dispatch, handler invoke, framing encode. |
| `http.stream` / `https.stream` | stream | stream | handler invoke, transport emit, stream close. |
| `http.sse` / `https.sse` | stream | SSE | encode event, emit event, close stream. |
| `ws` / `wss` / `websocket` | message | text or negotiated JSON-RPC | accept, decode, dispatch, handler, emit/close. |
| `webtransport` | session, stream, or datagram | WebTransport outer framing | lane-specific session, stream, or datagram rows with inner-framing validation. |

Unsupported or ambiguous bindings raise planning errors. For example, WebSocket bindings do not accept HTTP methods, HTTP JSON-RPC requires an RPC method, WebTransport request/response exchange is unsupported, and WebTransport outer framing must remain `webtransport`.

## Hook Ordering and Labels

The kernel orders security dependencies, dependencies, system hooks, user hooks, atoms, and handlers into phase plans. Labels are part of the diagnostics contract:

```text
PRE_HANDLER:secdep:myapp.auth.require_user
PRE_HANDLER:dep:myapp.context.load_tenant
HANDLER:hook:sys:handler:create@HANDLER
EGRESS_SHAPE:atom:wire:dump
```

Use labels to debug and test ordering. Do not use them as application APIs; use specs, decorators, dependencies, and hooks for configuration.

## Diagnostics and Traceability

Kernel plans feed `/system/kernelz` in concrete applications. Trace and measurement helpers make it possible to assert plan shape, count phase work, and inspect compiled execution without relying on a live server. This is especially important for transport work, where a route can look correct while the protocol chain is missing required event rows or capability masks.

## Best Practices

- Compile plans from explicit specs and bindings; do not guess transport behavior from URL strings alone.
- Keep protocol support checks fail-closed and close to planning.
- Preserve separate event rows for request, stream, message, session, and datagram families.
- Add tests at the kernel layer when changing hook order, labels, phase rows, protocol legality, or capability masks.
- Use measurement views for plan review instead of parsing private object internals.
- Keep runtime side effects out of kernel code; the kernel should plan, classify, and label, not perform IO.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-kernel
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-kernel"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_kernel")
print(module.__name__)
```

### Import a public symbol

```python
from tigrbl_kernel import BatchOpPlan

print(BatchOpPlan)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-kernel
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-kernel` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
- [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-base`](https://pypi.org/project/tigrbl-base/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)

## Documentation Links

- [Workspace docs](https://github.com/tigrbl/tigrbl/blob/master/docs/README.md)
- [Package catalog](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_CATALOG.md)
- [Package layout](https://github.com/tigrbl/tigrbl/blob/master/docs/developer/PACKAGE_LAYOUT.md)
- [Current target](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_TARGET.md)
- [Current state](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/CURRENT_STATE.md)
- [Next steps](https://github.com/tigrbl/tigrbl/blob/master/docs/conformance/NEXT_STEPS.md)
- [Documentation pointers](https://github.com/tigrbl/tigrbl/blob/master/docs/governance/DOC_POINTERS.md)
- [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json)
- [Release workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml)

## Support

- Community: [Discord](https://discord.gg/K4YTAPapjR).
- Issues: [GitHub Issues](https://github.com/tigrbl/tigrbl/issues).
- Repository: [pkgs/core/tigrbl_kernel](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_kernel).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-kernel`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
