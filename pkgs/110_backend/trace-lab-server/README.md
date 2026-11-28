# tigrbl-transport-trace-lab

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-transport-trace-lab</strong></p>
<p align="center">Tigrbl trace collector and monitor</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-transport-trace-lab/"><img alt="pypi: tigrbl-transport-trace-lab unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-transport-trace-lab%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/pyproject.toml"><img alt="Layer: 110_backend" src="https://img.shields.io/static/v1?label=Layer&amp;message=110_backend&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-transport-trace-lab/"><img alt="pypi downloads: tigrbl-transport-trace-lab: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-transport-trace-lab%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/README.md"><img alt="README hits: tigrbl-transport-trace-lab" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/110_backend/trace-lab-server/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/trace-lab-public.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/pkgs/110_backend/trace-lab-server/tests"><img alt="Tests: pytest suite" src="https://img.shields.io/static/v1?label=Tests&amp;message=pytest%20suite&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json"><img alt="Governance: registry" src="https://img.shields.io/static/v1?label=Governance&amp;message=registry&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/.ssot/evidence"><img alt="Evidence: test evidence" src="https://img.shields.io/static/v1?label=Evidence&amp;message=test%20evidence&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

The Python package runs a live transport scenario, exports Tigrbl identity events, and serves a separate PostgreSQL-backed trace monitor.

### Why This Package

The same Tigrbl app handles four protocols so the audience can follow their real runtime identities in one place.

### When to Use

Use it for engineering walkthroughs, identity-debugging sessions, and inspection of traces from a running Tigrbl app.

### Features

The scenario exercises REST, HTTP JSON-RPC, WebSocket JSON-RPC and WebTransport. The bounded demo capture records relationships to SQLite transactions and broker deliveries. The collector persists exported events and supports lookup by correlation ID.

### Non-Goals

The package focuses on Tigrbl identity events. Packet capture, telemetry emitted before Tigrbl dispatch, and automated retention scheduling are outside its scope.

---

## Getting Started

### Prerequisites

Use Git, Python 3.13, uv, Node 24 and pnpm 11. Run the commands from the workspace root. Collector mode also requires PostgreSQL.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`tigrbl-transport-trace-lab` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`tigrbl-transport-trace-lab` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`tigrbl-transport-trace-lab` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/tigrbl-transport-trace-lab
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/quick_start.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/docs/quick_start.sh).

```sh
pnpm install --frozen-lockfile
pnpm --filter @tigrbl/trace-lab-ui build
uv run --package tigrbl-transport-trace-lab tigrbl-trace-lab --frontend pkgs/130_frontend/trace-lab-ui/dist
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

Open the printed loopback address and select Run all transports. The dashboard shows live identities and their related events.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/verify.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/docs/verify.sh).

```sh
uv run --package tigrbl-trace-lab-demo pytest pkgs/110_backend/trace-lab-server/tests
```
<!-- readme-standards:end example.usage -->

### Configuration

Use `--host`, `--port`, and `--frontend` to configure the listener and supply the built Vite bundle.

Start the collector with `uv run --locked --package tigrbl-transport-trace-lab tigrbl-trace-lab --frontend pkgs/130_frontend/trace-lab-ui/dist`. The public demo guide lists the collector and exporter settings. [Monitor setup](../../170_examples/trace-lab-demo/README.md#configuration)

### Error Handling

A concurrent scenario receives 409. An invalid browser origin receives 403. A failed scenario returns a summary in the next snapshot and keeps any observed evidence.

The collector rejects invalid batches and deduplicates replayed events after commit. The exporter retries temporary failures in the background and counts dropped events.

### Best Practices

Inspect sequence and capture metadata alongside identity fields. Recorded timestamps show observation time. A producer that supports timing can also send monotonic durations for HTTP request entry to response start, engine transaction begin to commit or rollback, database flushes, operations, and hooks. Each flush carries its outcome and engine session ID. Its transaction ID is present when the engine observed a transaction.

For detailed execution traces on a Tigrbl version that supports atom timing, pass `trace_atoms=True` together with `trace_sink=exporter.capture` when creating the app. The executor measures each executed atom and identifies optimized fused work as one timing record. The exporter formats the compact atom batch in its worker. It counts dropped records when the export queue is full.

---

## Package Boundary

### What It Owns

The package owns the scenario, trace adapter, exporter, collector, and same-origin gateways. Tigrbl owns application execution and Tigrcorn owns the listeners.

### Public API and Import Surfaces

The `tigrbl-trace-lab` CLI starts the collector. It accepts batches at `POST /internal/trace/batches`, serves the paginated `GET /api/timeline`, and exposes recent or exact typed correlation lookups at `GET /api/correlations`. Import `TraceExporter` from `tigrbl_trace_transport` to attach the existing Tigrbl `trace_sink` callback in another app.

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `tigrbl-trace-lab` → `trace_lab.run:main`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The demo gateway receives the app, capture buffer, built frontend directory and scenario callable. The collector gateway receives its own Tigrbl app, the built frontend, and credentials. Each returns an ASGI callable.

### Protocol Consumers

The React UI consumes JSON over HTTP. The exporter sends JSON batches over HTTPS for remote deployments. The Python scenario clients exercise REST, HTTP JSON-RPC, WebSocket and WebTransport.

### Extensions

Add verified source observations to the snapshot adapter as additive fields and give them matching UI and contract tests.

---

## Operations and Readiness

### Operational Requirements

The demo runner uses local TCP and UDP ports, a temporary SQLite file and a temporary QUIC certificate. The collector serves HTTP and stores events in its configured PostgreSQL database.

### Health and Observability

`GET /demo/trace` exposes snapshot freshness, retained sequence bounds and the last scenario status. The exporter exposes `send_failures` and `dropped` counters on the worker instance and reports delivery failures in logs.

### Security and Resource Limits

The demo listeners bind to loopback. One scenario may execute at once, and the in-process capture retains at most 750 native records. The collector uses a bearer token for ingest and operator credentials for reads. The exporter holds a bounded queue in worker memory.

### Compatibility

The workspace guide identifies the pinned upstream revisions. The SQLite-backed collector tests exercise the same route bindings used by the PostgreSQL collector.

---

## Verification

### Tests

Run `uv run pytest` for the capture, gateway and collector tests. Set `TRACE_TEST_POSTGRES_URL` to a disposable database to enable the two-process monitor test. The CLI smoke test checks all four real transports and the bundled React assets.

### Certification Status

The package is development tooling. The registry records implementation and test evidence for the transport scenario.

### Evidence

The workspace SSOT registry links the feature to pytest and the four-transport smoke result.

---

## FAQ

### Why

A transport trace is easier to explain when the browser can follow real carrier and engine identities.

### How

Build the UI once, start the collector, then run Notes Pilot or the four-transport scenario in a separate process.

### When

Repeat the smoke test after updating upstream source pins or snapshot normalization. Run the PostgreSQL integration test after changing the collector schema or exporter behavior.

---

## Documentation and Related Packages

### More Documentation

This README is the package-local distribution entry point. See the [workspace docs](../../../docs/README.md), [current target](../../../docs/conformance/CURRENT_TARGET.md), [package catalog](../../../docs/developer/PACKAGE_CATALOG.md), and [layer layout](../../../docs/developer/PACKAGE_LAYOUT.md).

See the [public walkthrough](../../170_examples/trace-lab-demo/README.md) for setup and operational commands.

### Related Packages

The UI lives in [trace-lab-ui](../../130_frontend/trace-lab-ui). The workspace also depends on Tigrbl, Tigrcorn and tigr-asgi-contract.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-transport-trace-lab](https://pypi.org/project/tigrbl-transport-trace-lab/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Update the trace contract and its tests together when a change affects the UI payload.

### Development Setup

Install the locked uv and pnpm workspaces from the public repository root.

### Notes for Maintainers

Keep source overlays pinned and rerun the real scenario when changing them. Update SSOT evidence to match observed outcomes.

---

## Governance

### Ownership and Decision Making

The Tigrbl organization maintains the demo. The layered index declares package ownership and service direction.

### Standards and Policies

Readme-standards checks this guide. SSOT records claims and evidence. Ruff and pytest verify Python, while TypeScript and Vite verify the UI.

### Lifecycle and Migration

Coordinate additive changes to the trace API with the frontend adapter and recorded fixtures.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/110_backend/trace-lab-server/NOTICE) for attribution.
<!-- readme-standards:end notices -->
