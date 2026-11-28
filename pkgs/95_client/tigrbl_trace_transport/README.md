# tigrbl-trace-transport

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-trace-transport</strong></p>
<p align="center">HTTP export and canonical timeline projection for Tigrbl traces.</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace-transport/"><img alt="pypi: tigrbl-trace-transport unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-trace-transport%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/pyproject.toml"><img alt="Layer: 95_client" src="https://img.shields.io/static/v1?label=Layer&amp;message=95_client&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace-transport/"><img alt="pypi downloads: tigrbl-trace-transport: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-trace-transport%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/README.md"><img alt="README hits: tigrbl-trace-transport" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/95_client/tigrbl_trace_transport/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/readme-standards.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/pkgs/95_client/tigrbl_trace_transport/tests"><img alt="Tests: pytest suite" src="https://img.shields.io/static/v1?label=Tests&amp;message=pytest%20suite&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
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

Use the projector to build a trace timeline from native records. Use the exporter when the collector runs in a separate process.

### Features

The package provides canonical event projection, per-protocol counts, and bounded asynchronous HTTP export with deferred atom formatting.

### Non-Goals

The collector application owns persistence, query routes, and visualization.

---

## Getting Started

### Prerequisites

Use Python 3.10 through 3.14 and a Tigrbl source checkout that includes the shared trace field definitions. Exporting requires a wire v1 collector and its ingest token.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`tigrbl-trace-transport` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`tigrbl-trace-transport` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`tigrbl-trace-transport` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/tigrbl-trace-transport
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/readme/quick_start.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/docs/readme/quick_start.py).

```python
from tigrbl_trace_transport import project_event, projection_context

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
Source: [docs/readme/usage.py](https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/docs/readme/usage.py).

```python
from tigrbl_trace_transport import TraceExporter

exporter = TraceExporter("http://127.0.0.1:8766", "example-token", "notes", "local")

# Pass trace_sink=exporter.capture when constructing the Tigrbl app.
# Call exporter.start() at worker startup and await exporter.close() at shutdown.
assert callable(exporter.capture)
```
<!-- readme-standards:end example.usage -->

### Configuration

Provide the collector URL, bearer token, service name, and environment to `TraceExporter`. Enable `trace_atoms=True` on the Tigrbl app when per-atom samples are needed.

### Error Handling

Transient HTTP failures are retried with backoff. Permanent client errors and queue overflow increment the exporter drop counter.

### Best Practices

Create one exporter per server worker and close it during worker shutdown. Preserve native records when callers need to rebuild their own projections.

---

## Package Boundary

### What It Owns

The package owns wire v1 validation, HTTP export, canonical event projection, and canonical timeline summaries.

### Public API and Import Surfaces

Import `TraceExporter`, `ProjectionContext`, `TimelineRow`, `projection_context`, `project_event`, and `summarize` from `tigrbl_trace_transport`. Import `Batch` from `tigrbl_trace_transport.wire` on the collector.

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
- [Repository](https://github.com/tigrbl/tigrbl/tree/master/pkgs/95_client/tigrbl_trace_transport)
- [pypi: tigrbl-trace-transport](https://pypi.org/project/tigrbl-trace-transport/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Preserve wire v1 compatibility and add evidence for any change to public timeline event semantics.

### Development Setup

From the repository root, run `uv run --package tigrbl-trace-transport pytest pkgs/95_client/tigrbl_trace_transport`.

### Notes for Maintainers

Update the wire allowlist and legacy fixtures together when exposing a new trace field.

---

## Governance

### Ownership and Decision Making

Tigrbl maintains this package alongside the native trace contract and reviews changes through the repository's pull request process.

### Standards and Policies

The package follows the repository README policy and client-layer dependency rules.

### Lifecycle and Migration

Trace Lab consumers should switch imports to `tigrbl_trace_transport` and keep their collector URL, credentials, and stored captures.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/95_client/tigrbl_trace_transport/NOTICE) for attribution.
<!-- readme-standards:end notices -->
