# tigrbl-trace

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-trace</strong></p>
<p align="center">Wire validation and canonical timeline projection for Tigrbl traces.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace/"><img alt="pypi: tigrbl-trace unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-trace%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/pyproject.toml"><img alt="Layer: 010_core" src="https://img.shields.io/static/v1?label=Layer&amp;message=010_core&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace/"><img alt="pypi downloads: tigrbl-trace: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-trace%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/README.md"><img alt="README hits: tigrbl-trace" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/010_core/tigrbl_trace/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/pkgs/010_core/tigrbl_trace/tests"><img alt="Tests: pytest suite" src="https://img.shields.io/static/v1?label=Tests&amp;message=pytest%20suite&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/tools/readme/POLICY.md"><img alt="Governance: repository policy" src="https://img.shields.io/static/v1?label=Governance&amp;message=repository%20policy&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="Evidence: source and CI" src="https://img.shields.io/static/v1?label=Evidence&amp;message=source%20and%20CI&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Project native Tigrbl trace records into a canonical timeline and export them to a collector over HTTP.

### Why This Package

Trace consumers share event names, timing semantics, and the wire v1 batch contract.

### When to Use

Use the projector to build a trace timeline from native records and the wire schema to validate incoming batches.

### Features

The package provides wire validation, canonical event projection, and per-protocol counts.

### Non-Goals

The collector application owns persistence, query routes, and visualization.

---

## Getting Started

### Prerequisites

Use Python 3.10 through 3.14 and a Tigrbl source checkout that includes the shared trace field definitions.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`tigrbl-trace` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`tigrbl-trace` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`tigrbl-trace` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/tigrbl-trace
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/docs/readme/quick_start.py).

```python
from tigrbl_trace import project_event, projection_context

native = {
    "sequence": 1,
    "at": "2026-01-01T00:00:00+00:00",
    "kind": "Transaction",
    "transport": "REST",
    "outcome": "begin",
    "engine_session_id": "session",
    "transaction_id": "transaction",
}
event = project_event(native, projection_context([native]))
assert event is not None and event["kind"] == "db.tx.begin"
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

The transaction begin record projects to an event with kind `db.tx.begin`.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/docs/readme/usage.py).

```python
from tigrbl_trace import project_event, projection_context

native = {
    "sequence": 1,
    "at": "2026-01-01T00:00:00+00:00",
    "kind": "Transaction",
    "transport": "REST",
    "outcome": "begin",
    "engine_session_id": "session",
    "transaction_id": "transaction",
}
event = project_event(native, projection_context([native]))
assert event is not None and event["kind"] == "db.tx.begin"
```
<!-- readme-standards:end example.usage -->

### Configuration

Pass native trace records to projection_context and project_event.

### Error Handling

Wire validation rejects malformed event envelopes.

### Best Practices

Preserve native records when callers need to rebuild their own projections.

---

## Package Boundary

### What It Owns

The package owns wire v1 validation, HTTP export, canonical event projection, and canonical timeline summaries.

### Public API and Import Surfaces

Import `TraceExporter`, `ProjectionContext`, `TimelineRow`, `projection_context`, `project_event`, and `summarize` from `tigrbl_trace`. Import `Batch` from `tigrbl_trace.wire` on the collector.

### Entry Points

<!-- readme-standards:begin entry-points -->
This package declares no command-line, GUI, or plugin entry points in its manifest.
<!-- readme-standards:end entry-points -->

### Injected Dependencies

Tigrbl supplies native events through the trace sink callback. The application supplies its collector configuration and worker lifecycle.

### Protocol Consumers

Deploy an HTTP receiver that accepts authenticated POST requests at `/internal/trace/batches` and validates the wire v1 envelope.

### Extensions

A collector may decorate projected rows with storage timestamps or source metadata. Use `projection_context` to supply related native events.

---

## Operations and Readiness

### Operational Requirements

Start and close the exporter on the event loop that owns the worker. Both services must agree on the ingest token.

### Health and Observability

Observe `dropped` and `send_failures` per exporter. Collector health and persistence metrics belong to the deployed collector.

### Security and Resource Limits

Export permits HTTPS and loopback HTTP. Wire validation forwards allowlisted scalar values, bounds field lengths, and limits batches to 50 events.

### Compatibility

Wire v1 and existing event field names are preserved. Historic HTTP traces can still use the `/rpc` path fallback if related dispatch records are unavailable.

---

## Verification

### Tests

The package tests exercise legacy wire v1 validation, protocol attribution, timeline timing, and transaction counts. README examples are executable tests.

### Certification Status

This source package carries no certification claim.

### Evidence

The package tests and Trace Lab integration tests provide evidence for projection and exporter compatibility.

---

## FAQ

### Why

The same trace can be read from a bounded timeline or a collector table and produce consistent event and duration fields.

### How

Build a context from the available native rows, pass it to `project_event`, then call `summarize` on the projected rows.

### When

Use remote export for an independent collector. Use the Tigrbl `Timeline` sink for capture within one process.

---

## Documentation and Related Packages

### More Documentation

See Trace Lab's workspace guide for deployment and collector configuration.

This README is the package-local distribution entry point. See the repository
[documentation](../../../docs/README.md), [current conformance target](../../../docs/conformance/CURRENT_TARGET.md),
[package catalog](../../../docs/developer/PACKAGE_CATALOG.md), [package layout](../../../docs/developer/PACKAGE_LAYOUT.md),
and [SSOT registry](../../../.ssot/registry.json).

### Related Packages

`tigrbl-typing` defines native trace fields, and `tigrbl` owns instrumentation and the in-process `Timeline` sink.

### Project Links

<!-- readme-standards:begin project-links -->
- [Issues](https://github.com/tigrbl/tigrbl/issues)
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/010_core/tigrbl_trace)
- [pypi: tigrbl-trace](https://pypi.org/project/tigrbl-trace/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Preserve wire v1 compatibility and add evidence for any change to public timeline event semantics.

### Development Setup

From the repository root, run `uv run --package tigrbl-trace pytest pkgs/010_core/tigrbl_trace`.

### Notes for Maintainers

Update the wire allowlist and legacy fixtures together when exposing a new trace field.

---

## Governance

### Ownership and Decision Making

Tigrbl maintains this package alongside the native trace contract and reviews changes through the repository's pull request process.

### Standards and Policies

The package follows the repository README policy and client-layer dependency rules.

### Lifecycle and Migration

Trace Lab consumers should switch imports to `tigrbl_trace` and keep their collector URL, credentials, and stored captures.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/010_core/tigrbl_trace/NOTICE) for attribution.
<!-- readme-standards:end notices -->
