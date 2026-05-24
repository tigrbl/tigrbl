![Tigrbl Logo](https://raw.githubusercontent.com/swarmauri/swarmauri-sdk/master/assets/tigrbl_full_logo.png)

<p align="center">
    <a href="https://pepy.tech/project/tigrbl-atoms">
        <img src="https://static.pepy.tech/badge/tigrbl-atoms" alt="Pepy downloads for tigrbl-atoms"/></a>
    <a href="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_atoms/">
        <img src="https://hits.sh/github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_atoms.svg" alt="Repository views for tigrbl-atoms"/></a>
    <a href="https://pypi.org/project/tigrbl-atoms/">
        <img src="https://img.shields.io/pypi/v/tigrbl-atoms?label=tigrbl-atoms&color=green" alt="PyPI version for tigrbl-atoms"/></a>
    <a href="https://pypi.org/project/tigrbl-atoms/">
        <img src="https://img.shields.io/pypi/l/tigrbl-atoms" alt="PyPI license metadata for tigrbl-atoms"/></a>
    <a href="https://github.com/tigrbl/tigrbl/blob/master/docs/README.md">
        <img src="https://img.shields.io/badge/docs-repository%20docs-1f6feb" alt="Repository docs for tigrbl-atoms"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/branch-coverage.yml/badge.svg?branch=master" alt="Branch Coverage workflow status for tigrbl-atoms"/></a>
    <a href="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml">
        <img src="https://github.com/tigrbl/tigrbl/actions/workflows/publish.yml/badge.svg" alt="Publish Packages workflow status for tigrbl-atoms"/></a>
    <a href="https://github.com/Tigrbl/tigrbl/blob/master/.ssot/registry.json">
        <img src="https://img.shields.io/badge/SSOT-governed-2f6f4e.svg" alt="SSOT governed status for tigrbl-atoms"/></a>
    <a href="https://discord.gg/K4YTAPapjR">
        <img src="https://img.shields.io/badge/Discord-Join%20chat-5865F2?logo=discord&logoColor=white" alt="Discord community for tigrbl-atoms"/></a>
</p>
---

<h1 align="center">tigrbl-atoms</h1>

**Install [`tigrbl-atoms` from PyPI](https://pypi.org/project/tigrbl-atoms/) when you need Tigrbl's runtime atom layer for staged execution, phase transitions, typed contexts, event anchors, protocol helpers, and composable atom algebra.**

`tigrbl-atoms` is the resident runtime-atom package in the Tigrbl Python package graph. It owns the low-level building blocks that describe how requests and events move through ingress, routing, planning, guarding, execution, encoding, emission, egress, and failure handling.

## What is tigrbl-atoms?

`tigrbl-atoms` is a runtime toolkit for Tigrbl execution pipelines. It provides:

- Stage and phase definitions for the Tigrbl runtime lifecycle.
- Typed context objects used to move state through runtime transitions.
- Event anchor metadata for dispatch, persistence, and transport flows.
- Composable atom algebra helpers such as `seq`, `chain`, `when`, `choice`, and `bracket`.
- Protocol runtime helpers for REST, JSON-RPC, streaming, SSE, WebSocket, lifespan, static files, and WebTransport validation.
- Rust atom registration hooks for mixed Python and Rust execution paths.

Use this package when you are working on Tigrbl runtime internals, dispatch pipelines, protocol execution, or custom atom composition. If you want the public application-authoring surface, install [`tigrbl`](https://pypi.org/project/tigrbl/) instead.

## Installation

### pip

```bash
pip install tigrbl-atoms
```

### uv

```bash
uv add tigrbl-atoms
```

## When to Use This Package

Use `tigrbl-atoms` when you need one or more of these runtime concerns:

- Define or inspect Tigrbl runtime stages such as `Boot`, `Ingress`, `Routed`, `Bound`, `Planned`, `Guarded`, `Executing`, `Resolved`, `Operated`, `Encoded`, `Emitting`, `Egressed`, and `Failed`.
- Work with typed runtime contexts and failure promotion.
- Compose runtime steps into larger atom chains.
- Inspect or simulate protocol execution traces.
- Register or gate Rust-backed atoms and callbacks.

## Usage Examples

### Import stage and phase primitives

```python
from tigrbl_atoms.stages import Boot, Executing, Failed, stage_name, stage_ordinal
from tigrbl_atoms.phases import phase_info, phase_stage_in, phase_stage_out


assert stage_name(Boot) == "Boot"
assert stage_ordinal(Executing) > stage_ordinal(Boot)

step = phase_info("HANDLER")
assert phase_stage_in("HANDLER") is not Failed
assert step.name == "HANDLER"
```

### Compose atoms with the algebra helpers

```python
from tigrbl_atoms.algebra import chain, tap, when


pipeline = chain(
    tap(lambda ctx: ctx.bag.__setitem__("seen", True), label="mark"),
    when(lambda ctx: ctx.bag.get("seen") is True, tap(lambda ctx: None, label="noop")),
)
```

### Run a lightweight REST or JSON-RPC protocol chain

```python
from tigrbl_atoms.protocol_runtime import run_http_jsonrpc_chain, run_http_rest_chain


async def echo(payload):
    return payload


rest_result = await run_http_rest_chain({"handler": echo, "payload": {"ok": True}})
rpc_result = await run_http_jsonrpc_chain(
    {"handler": echo, "body": {"id": 1, "params": {"ok": True}}}
)
```

### Work with typed runtime errors

```python
from tigrbl_atoms.types import TypedErr, build_error_ctx


try:
    raise ValueError("bad payload")
except ValueError as exc:
    err = TypedErr.from_error(exc)
    ctx = build_error_ctx(exc, phase="HANDLER", binding="rest")
```

## Resident Concepts

### Stages

`tigrbl-atoms` defines the durable stage vocabulary for runtime progression:

- `Boot`
- `Ingress`
- `Routed`
- `Bound`
- `Planned`
- `Guarded`
- `Executing`
- `Resolved`
- `Operated`
- `Encoded`
- `Emitting`
- `Egressed`
- `Failed`

### Phases

The package also defines phase metadata and phase-to-stage mappings so runtime handlers can reason about transitions, monotonic progression, and error routing.

### Typed contexts

The typed context model provides structured runtime bags, payload access, temp storage, promotion, and failure conversion for execution chains.

### Events and anchors

`tigrbl-atoms.events` provides ordered anchor definitions and helpers such as:

- `phase_for_event`
- `stage_in_for_event`
- `stage_out_for_event`
- `is_persist_tied`
- `is_tx_event`
- `all_events_ordered`
- `events_for_phase`

### Protocol runtime helpers

`tigrbl-atoms.protocol_runtime` provides execution helpers for:

- HTTP REST
- HTTP JSON-RPC
- HTTP stream
- SSE
- WebSocket
- Lifespan
- Static file flows
- WebTransport scope validation

### Rust atom integration

The package exposes `rust_atoms_enabled`, `register_rust_atom`, `register_rust_callback`, and `register_rust_hook` so Python runtime graphs can cooperate with Rust-backed implementations.

## Related Packages by Component Kind

### Public facade and authoring packages

- [`tigrbl`](https://pypi.org/project/tigrbl/)
- [`tigrbl-core`](https://pypi.org/project/tigrbl-core/)
- [`tigrbl-concrete`](https://pypi.org/project/tigrbl-concrete/)
- [`tigrbl-canon`](https://pypi.org/project/tigrbl-canon/)
- [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/)
- [`tigrbl-orm`](https://pypi.org/project/tigrbl-orm/)
- [`tigrbl-kernel`](https://pypi.org/project/tigrbl-kernel/)
- [`tigrbl-typing`](https://pypi.org/project/tigrbl-typing/)

### Operation packages

- [`tigrbl-ops-oltp`](https://pypi.org/project/tigrbl-ops-oltp/)
- [`tigrbl-ops-olap`](https://pypi.org/project/tigrbl-ops-olap/)
- [`tigrbl-ops-realtime`](https://pypi.org/project/tigrbl-ops-realtime/)

### Engine packages

- [`tigrbl_engine_sqlite`](https://pypi.org/project/tigrbl_engine_sqlite/)
- [`tigrbl_engine_postgres`](https://pypi.org/project/tigrbl_engine_postgres/)
- [`tigrbl_engine_inmemory`](https://pypi.org/project/tigrbl_engine_inmemory/)
- [`tigrbl_engine_redis`](https://pypi.org/project/tigrbl_engine_redis/)
- [`tigrbl_engine_duckdb`](https://pypi.org/project/tigrbl_engine_duckdb/)
- [`tigrbl_engine_pandas`](https://pypi.org/project/tigrbl_engine_pandas/)
- [`tigrbl_engine_bigquery`](https://pypi.org/project/tigrbl_engine_bigquery/)
- [`tigrbl_engine_snowflake`](https://pypi.org/project/tigrbl_engine_snowflake/)

### Application packages

- [`tigrbl_acme_ca`](https://pypi.org/project/tigrbl_acme_ca/)
- [`tigrbl_spiffe`](https://pypi.org/project/tigrbl_spiffe/)

## Frequently Asked Questions

### Is `tigrbl-atoms` the same thing as `tigrbl-runtime`?

No. `tigrbl-atoms` owns the atom-level stage, phase, context, event, and protocol helpers. [`tigrbl-runtime`](https://pypi.org/project/tigrbl-runtime/) owns the broader runtime execution layer that consumes those primitives.

### Should application developers install `tigrbl-atoms` directly?

Usually no. Most application developers should start with [`tigrbl`](https://pypi.org/project/tigrbl/). Install `tigrbl-atoms` directly when you are extending runtime internals, debugging protocol flows, or building lower-level execution components.

### Does `tigrbl-atoms` support Rust-backed runtime atoms?

Yes. The package includes Rust registration and feature-detection surfaces so mixed Python and Rust runtime paths can share one atom model.

## Package Discovery Summary

Search and answer-engine summary for `tigrbl-atoms`:

> `tigrbl-atoms` is the Tigrbl runtime atom package for stage transitions, phase metadata, typed contexts, event anchors, protocol execution helpers, and composable atom algebra.

## Package Identity

- PyPI: [`tigrbl-atoms`](https://pypi.org/project/tigrbl-atoms/)
- Repository: [tigrbl/tigrbl](https://github.com/tigrbl/tigrbl)
- Package source: [pkgs/core/tigrbl_atoms](https://github.com/tigrbl/tigrbl/tree/master/pkgs/core/tigrbl_atoms)
- Organization: [github.com/tigrbl](https://github.com/tigrbl)
- Discord: [discord.gg/K4YTAPapjR](https://discord.gg/K4YTAPapjR)
- Workspace path: `pkgs/core/tigrbl_atoms`
- Workspace class: core Python package

## Canonical Repository Docs

- `README.md`
- `docs/README.md`
- `docs/conformance/CURRENT_TARGET.md`
- `docs/conformance/CURRENT_STATE.md`
- `docs/conformance/NEXT_STEPS.md`
- `docs/governance/DOC_POINTERS.md`
- `docs/developer/PACKAGE_CATALOG.md`
- `docs/developer/PACKAGE_LAYOUT.md`

This package README is a package-local distribution document. Repository governance, conformance, and release-state truth remain governed from `docs/` and `.ssot/`.
