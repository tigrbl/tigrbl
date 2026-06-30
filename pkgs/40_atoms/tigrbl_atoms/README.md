<div align="center">
<h1>tigrbl-atoms</h1>
<img src="https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png" alt="Tigrbl logo" width="140"/>
<p><strong>Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.</strong></p>
<a href="https://pypi.org/project/tigrbl-atoms/"><img src="https://img.shields.io/pypi/v/tigrbl-atoms?label=PyPI" alt="PyPI version for tigrbl-atoms"/></a>
<a href="https://pypi.org/project/tigrbl-atoms/"><img src="https://static.pepy.tech/badge/tigrbl-atoms" alt="Downloads for tigrbl-atoms"/></a>
<a href="https://discord.gg/K4YTAPapjR"><img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-atoms"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/README.md"><img src="https://hits.sh/github.com/tigrbl/tigrbl/blob/master/pkgs/40_atoms/tigrbl_atoms/README.md.svg?label=hits" alt="Repository hits for tigrbl-atoms README"/></a>
<a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache%202.0-525252" alt="Apache 2.0 license"/></a>
<a href="pyproject.toml"><img src="https://img.shields.io/badge/python-3.10%2C%203.11%2C%203.12%2C%203.13%2C%203.14-3776ab" alt="Python versions 3.10 | 3.11 | 3.12 | 3.13 | 3.14 for tigrbl-atoms"/></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md"><img src="https://img.shields.io/badge/workspace-core-1f6feb" alt="Workspace group for tigrbl-atoms"/></a>
</div>

## What is tigrbl-atoms?

Runtime atom package for Tigrbl stages, phases, typed contexts, event anchors, protocol execution, and composable pipeline algebra.

## Why use tigrbl-atoms?

Use it when you need this foundational Tigrbl layer directly as a small, focused dependency.

## When should I install tigrbl-atoms?

Install it for extension packages, package-local tests, or internals that need this boundary without the whole facade.

## Who is tigrbl-atoms for?

Framework maintainers, extension authors, and advanced users composing Tigrbl from split packages.

## Where does tigrbl-atoms fit?

`tigrbl-atoms` lives at `pkgs/40_atoms/tigrbl_atoms` and serves a focused layer in the split Tigrbl framework.

## How does tigrbl-atoms work?

It owns a narrow layer in the split workspace and is consumed by higher-level packages through explicit dependencies.


## Install

```bash
uv add tigrbl-atoms
```

```bash
pip install tigrbl-atoms
```

## Surface Coverage

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

## What It Owns

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

## Public API and Import Surface

- Import roots: `tigrbl_atoms`.
- Public symbols: `EGRESS_PHASES`, `EdgeTarget`, `ErrorCtx`, `HANDLER_PHASES`, `HookPhase`, `HookPhases`, `HookPredicate`, `INGRESS_PHASES`, `PHASE_SEQUENCE`, `PhaseTreeEdge`, `PhaseTreeNode`, `StepFn`.
- Workspace dependencies: [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/), [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/), [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/), [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/), [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/).
- External runtime dependencies: `jinja2>=3.1`, `sqlalchemy>=2.0`, `typing-extensions>=4.0`.

## Lifecycle Phases

Atoms are organized around the runtime lifecycle:

| Group | Phases | Meaning |
|---|---|---|
| Ingress | `INGRESS_BEGIN`, `INGRESS_PARSE`, `INGRESS_DISPATCH` | Receive a transport unit, initialize context, parse input, and resolve the target binding/operation. |
| Transaction and handler | `PRE_TX_BEGIN`, `START_TX`, `PRE_HANDLER`, `HANDLER`, `POST_HANDLER`, `PRE_COMMIT`, `TX_COMMIT` | Prepare policy, open or attach transaction state, validate input, run handlers, post-process, and commit when Tigrbl owns the transaction. |
| Egress | `POST_COMMIT`, `EGRESS_SHAPE`, `EGRESS_FINALIZE`, `POST_RESPONSE` | Shape output, apply response rules, finalize transport output, and run after-response work. |
| Error | `ON_ERROR`, phase-specific `ON_*_ERROR`, `TX_ROLLBACK` | Classify errors, shape error responses, and roll back transaction-owned work. |

`END_TX`, `ON_END_TX_ERROR`, and `ON_ROLLBACK` are compatibility aliases for `TX_COMMIT`, `ON_TX_COMMIT_ERROR`, and `TX_ROLLBACK`. New docs and new atoms should use the current names.

## Atom Semantics

An atom is a small, named runtime unit. It should do one thing, take context from the compiled plan, and leave the context in the expected next stage. Atoms are intentionally smaller than handlers:

- ingress atoms do not perform persistence;
- dispatch atoms do not execute business logic;
- wire atoms do not choose transport routes;
- storage atoms do not commit transactions;
- egress atoms do not reopen handler work;
- error atoms should be deterministic and avoid masking the original failure unless policy requires it.

This separation lets the kernel produce readable labels, lets diagnostics explain execution order, and lets runtime transports share behavior across REST, JSON-RPC, stream, SSE, WebSocket, WSS, and WebTransport surfaces.

## System Handler Catalog

The `atoms/sys` package contains default handlers and transaction units used by operation packs and runtime plans. The catalog includes scalar CRUD handlers (`create`, `read`, `update`, `replace`, `merge`, `delete`, `list`, `clear`), bulk handlers, analytical handlers (`count`, `exists`, `aggregate`, `group_by`), realtime handlers (`publish`, `subscribe`, `tail`), stream/file handlers (`upload`, `download`, `append_chunk`, `checkpoint`), custom/no-op handlers, persistence helpers, and transaction helpers such as `start_tx`, `phase_db`, and `commit_tx`.

Use system handlers when implementing framework behavior. Application code should normally reach these through operations on a Tigrbl app or model rather than importing a handler atom directly.

## Transaction Discipline

Transaction atoms and database guards exist so user hooks and system handlers do not silently commit or flush at the wrong phase. The broad rule is:

- before `START_TX`, do not assume a database transaction exists;
- from `START_TX` through `PRE_COMMIT`, in-transaction validation and handler work may proceed under guards;
- `TX_COMMIT` owns final commit when Tigrbl owns the transaction;
- `POST_COMMIT`, `EGRESS_*`, and `POST_RESPONSE` should not mutate transaction-owned state;
- `TX_ROLLBACK` performs rollback and cleanup for failures.

If you add or modify an atom, make its transaction expectations explicit in tests. Do not hide direct session commits inside validation, response, transport, or error atoms.

## Transport and Protocol Atoms

Transport atoms model runtime units instead of broad protocol names. A WebSocket message, an SSE event, an HTTP stream chunk, and a WebTransport datagram are different units even when they carry similar payloads. Keep family, exchange, framing, lane, subevent, and handler intent separate.

Practical guidance:
- Use ingress/dispatch atoms to parse and resolve transport units.
- Use protocol/runtime helpers to carry channel metadata.
- Use response and egress atoms to render or emit units.
- Preserve fail-closed behavior for unsupported protocol/framing/lane combinations.

## Extension Guidance

- Add atoms when the behavior is reusable, phase-specific, and independently testable.
- Keep application policy in hooks or dependencies, not in generic atoms.
- Keep atom names stable and descriptive; they show up in kernel diagnostics.
- Avoid broad atoms that parse, validate, execute, persist, and render at once.

## Usage Examples

### Verify the installed package

```bash
python -m pip show tigrbl-atoms
python - <<'PY'
from importlib.metadata import version
print(version("tigrbl-atoms"))
PY
```

### Import the package boundary

```python
import importlib

module = importlib.import_module("tigrbl_atoms")
print(module.__name__)
```

### Import a public symbol

```python
from tigrbl_atoms import EGRESS_PHASES

print(EGRESS_PHASES)
```

### Use with the facade when building applications

```bash
uv add tigrbl tigrbl-atoms
python - <<'PY'
import tigrbl
print(tigrbl.__name__)
PY
```

## How To Choose This Package

Choose `tigrbl-atoms` when the quick-answer table matches your use case. Choose [`tigrbl`](https://pypi.org/project/tigrbl/) instead when you want the full public facade. Choose a lower-level package such as [`tigrbl-core`](https://pypi.org/project/tigrbl-core/), [`tigrbl-base`](https://pypi.org/project/tigrbl-base/), or [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) when you are building framework extensions or testing a specific internal boundary.

## Related Packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)
- [`tigrbl-ops-webtransport`](https://pypi.org/project/tigrbl-ops-webtransport/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)
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
- Repository: [pkgs/40_atoms/tigrbl_atoms](https://github.com/tigrbl/tigrbl/tree/master/pkgs/40_atoms/tigrbl_atoms).

## Package-local Boundary

This file is a package-local distribution entry point. This README is the package-local distribution entry point for `tigrbl-atoms`. It answers install, usage, API, ownership, and certification-orientation questions for this package. Broader architectural decisions, release status, and cross-package proof chains remain in the repository-level docs and SSOT registry.

## Certification Status

- Package status: governed package in the `tigrbl/tigrbl` workspace.
- Governance source: [SSOT registry](https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json).
- Release evidence: [publish workflow](https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml) validates package builds, tests, GitHub release assets, and PyPI publication for managed packages.
- Local certification guard: `pkgs/97_tests/tigrbl_tests/tests/unit/test_package_badges_and_notices.py` verifies every package README keeps the Discord badge, Apache 2.0 badge, explicit Python-version badge, `LICENSE`, and `NOTICE`.
- Scope note: this README documents the package boundary. Runtime feature support remains governed by `.ssot/` entities and the conformance docs linked below.

## License

Licensed under the Apache License, Version 2.0. See `LICENSE`, `NOTICE`, and the official [Apache 2.0 license text](https://www.apache.org/licenses/LICENSE-2.0).
