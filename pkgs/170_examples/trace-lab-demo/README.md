# tigrbl-trace-lab-demo

<!-- readme-standards:begin branding -->
<p align="center"><a href="https://github.com/tigrbl/tigrbl"><img src="https://raw.githubusercontent.com/tigrbl/tigrbl/master/assets/tigrbl.brand.theme.svg" alt="Tigrbl" width="300"></a></p>
<p align="center"><strong>tigrbl-trace-lab-demo</strong></p>
<p align="center">Public Trace Lab walkthrough and Notes Pilot</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace-lab-demo/"><img alt="pypi: tigrbl-trace-lab-demo unpublished" src="https://img.shields.io/static/v1?label=pypi&amp;message=tigrbl-trace-lab-demo%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/pyproject.toml"><img alt="Source version: 0.1.0" src="https://img.shields.io/static/v1?label=Source%20version&amp;message=0.1.0&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/pyproject.toml"><img alt="Python: &gt;=3.10,&lt;3.15" src="https://img.shields.io/static/v1?label=Python&amp;message=%3E%3D3.10%2C%3C3.15&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/pyproject.toml"><img alt="Layer: 170_examples" src="https://img.shields.io/static/v1?label=Layer&amp;message=170_examples&amp;labelColor=1E293B&amp;color=6D28D9"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/README.md#lifecycle-and-migration"><img alt="Lifecycle: active" src="https://img.shields.io/static/v1?label=Lifecycle&amp;message=active&amp;labelColor=1E293B&amp;color=166534"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/LICENSE"><img alt="License: Apache-2.0" src="https://img.shields.io/static/v1?label=License&amp;message=Apache-2.0&amp;labelColor=1E293B&amp;color=86198F"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/NOTICE"><img alt="Notice: attribution" src="https://img.shields.io/static/v1?label=Notice&amp;message=attribution&amp;labelColor=1E293B&amp;color=86198F"></a>
</p>
<p align="center">
<a href="https://pypi.org/project/tigrbl-trace-lab-demo/"><img alt="pypi downloads: tigrbl-trace-lab-demo: unpublished" src="https://img.shields.io/static/v1?label=pypi%20downloads&amp;message=tigrbl-trace-lab-demo%3A%20unpublished&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/README.md"><img alt="README hits: tigrbl-trace-lab-demo" src="https://hits.sh/github.com/tigrbl/tigrbl/pkgs/170_examples/trace-lab-demo/README.md.svg?label=README%20hits&amp;labelColor=1E293B&amp;color=0E7490"></a>
</p>
<p align="center">
<a href="https://github.com/tigrbl/tigrbl/actions/workflows/verify.yml"><img alt="README standards: CI gate" src="https://img.shields.io/static/v1?label=README%20standards&amp;message=CI%20gate&amp;labelColor=1E293B&amp;color=1D4ED8"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/pkgs/170_examples/trace-lab-demo/tests"><img alt="Tests: pytest suite" src="https://img.shields.io/static/v1?label=Tests&amp;message=pytest%20suite&amp;labelColor=1E293B&amp;color=0F766E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/README.md#certification-status"><img alt="Certification: not certified" src="https://img.shields.io/static/v1?label=Certification&amp;message=not%20certified&amp;labelColor=1E293B&amp;color=92400E"></a>
<a href="https://github.com/tigrbl/tigrbl/blob/master/.ssot/registry.json"><img alt="Governance: registry" src="https://img.shields.io/static/v1?label=Governance&amp;message=registry&amp;labelColor=1E293B&amp;color=4338CA"></a>
<a href="https://github.com/tigrbl/tigrbl/tree/master/.ssot/evidence"><img alt="Evidence: test evidence" src="https://img.shields.io/static/v1?label=Evidence&amp;message=test%20evidence&amp;labelColor=1E293B&amp;color=6D28D9"></a>
</p>
<p align="center"><a href="#overview">Overview</a> · <a href="#installation">Installation</a> · <a href="#quick-start">Quick Start</a> · <a href="#usage">Usage</a> · <a href="#public-api-and-import-surfaces">API</a> · <a href="#contributing">Contributing</a> · <a href="#governance">Governance</a> · <a href="#license">License</a></p>
<!-- readme-standards:end branding -->

---

## Overview

### Summary

Run real REST, HTTP JSON-RPC, WebSocket JSON-RPC and WebTransport traffic from one browser dashboard. The React UI shows a karyogram, event table, linked identity inspector and distributions.

### Why This Package

The same dashboard can inspect transport identities, Tigrbl invocations, and the database and broker events related to them.

### When to Use

Use the scenario for interactive transport walkthroughs and the collector to inspect a running Tigrbl service.

### Features

The scenario runs four transports against one local app. The separate collector stores Tigrbl identity events in PostgreSQL and supports correlation-ID lookup.

### Non-Goals

Collection is limited to events emitted by Tigrbl and its configured broker. The workspace excludes packet capture and Tigrcorn events that occur upstream of the app.

---

## Getting Started

Run from the public Tigrbl workspace. The framework, collector, and UI are available in that checkout.
For a Tigrbl revision available in a local checkout, use
Run `uv run --no-project --python 3.13 python tools/checkout_trace_lab_sources.py` for the pinned public Tigrcorn and ASGI contract sources used by the four-transport scenario.

### Prerequisites

Python 3.13, uv, Git, Node 24 and pnpm 11. The monitor also requires PostgreSQL.

### Installation

#### uv

<!-- readme-standards:begin installation.uv -->
`tigrbl-trace-lab-demo` is not declared published. From the source checkout:

```bash
uv pip install .
```
<!-- readme-standards:end installation.uv -->

#### pip

<!-- readme-standards:begin installation.pip -->
`tigrbl-trace-lab-demo` is not declared published. From the source checkout:

```bash
python -m pip install .
```
<!-- readme-standards:end installation.pip -->

#### Poetry

<!-- readme-standards:begin installation.poetry -->
`tigrbl-trace-lab-demo` is not declared published. From a separate Poetry project, replace the path with your checkout:

```bash
poetry add /path/to/tigrbl-trace-lab-demo
```
<!-- readme-standards:end installation.poetry -->

### Quick Start

#### Example

<!-- readme-standards:begin example.quick-start -->
Source: [docs/quick_start.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/docs/quick_start.sh).

```sh
uv run --no-project --python 3.13 python tools/checkout_trace_lab_sources.py
pnpm install --frozen-lockfile
pnpm --filter @tigrbl/trace-lab-ui build
uv run --locked --package tigrbl-trace-lab-demo tigrbl-trace-lab-demo --port 0 --smoke
```
<!-- readme-standards:end example.quick-start -->

#### Expected Result

Open the loopback URL printed by the server, then select **Run all transports**. The scenario writes and reads a note, confirms a WebSocket publication reaches its subscriber, and sends a framed JSON-RPC invocation and datagrams over WebTransport. Use `--port 0 --quic-port 0` for automatically assigned ports. The browser connects to the Python server for both the bundle and APIs. The QUIC test client runs server-side.

---

## Usage

### Common Workflows

<!-- readme-standards:begin example.usage -->
Source: [docs/verify.sh](https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/docs/verify.sh).

```sh
uv run --package tigrbl-trace-lab-demo pytest pkgs/170_examples/trace-lab-demo/tests
```
<!-- readme-standards:end example.usage -->

### Configuration

**Run the trace monitor.** Build the lab and prepare its pinned sources using Quick Start. Start a separate PostgreSQL database for `timeline_events` and set the following variables in the collector process.

| Variable | Value |
| --- | --- |
| `TRACE_DATABASE_URL` | Dedicated `postgresql+psycopg://user:password@host:5432/database` DSN. The startup role needs permission to create the timeline table and indexes on first run. |
| `TRACE_INGEST_TOKEN` | Shared secret for exporter processes. |
| `TRACE_OPERATOR_USER`, `TRACE_OPERATOR_PASSWORD` | Browser credentials for the monitor and read API. |

Run `uv run --locked --package tigrbl-transport-trace-lab tigrbl-trace-lab --frontend pkgs/130_frontend/trace-lab-ui/dist`. The collector binds to loopback by default. For a remote deployment, put the collector behind an HTTPS reverse proxy and configure the exporter with that HTTPS origin.

In a second process, set `TRACE_COLLECTOR_URL=http://127.0.0.1:8766` and the same `TRACE_INGEST_TOKEN`, then run `uv run --locked --package tigrbl-trace-lab-demo notes-pilot` for the independent REST producer or `uv run --locked --package tigrbl-trace-lab-demo tigrbl-trace-lab-demo` for the four-transport scenario. Set `TRACE_SERVICE` and `TRACE_ENVIRONMENT` to label each source in the event inspector. Open the primary lab and run the ordinary transport scenario. Open the collector in a separate tab and sign in with the operator credentials. To inspect an individual request, paste its `x-correlation-id` into **Find an ID** on the Events tab.

**Wire an existing Tigrbl app.** Use the `TraceExporter` from `tigrbl_trace_transport` in the app's environment and create it inside each server worker. Call `start()` in the startup lifecycle, register `exporter.capture` as the app's `trace_sink`, and `await exporter.close()` during shutdown. Pass the same callback to a realtime broker you instantiate explicitly.

**Inspect operations and hooks.** With a Tigrbl checkout that emits execution timing, the correlation waterfall labels each operation by its table model and resolved alias, such as `PilotNote.create`. Expand the operation to see executed hooks grouped by lifecycle phase. Hover a bar for the name, outcome, and duration. Tigrbl measures operation execution and each hook callback on the producer's monotonic clock. The example uses the Tigrbl packages from the current public workspace checkout.

### Error Handling

`POST /demo/run` refuses overlapping requests. The exporter retries the current batch during a temporary collector outage. The in-memory queue tracks drops when it fills.

### Best Practices

Use correlation IDs to inspect individual requests. Timeline timestamps indicate when records were captured. Recorded sample distributions are synthetic and visibly labeled.

---

## Package Boundary

### What It Owns

| Layer | Package | Responsibility |
| --- | --- | --- |
| `110_backend` | `pkgs/110_backend/trace-lab-server` | PostgreSQL collector, query API, and same-origin gateway |
| `130_frontend` | `pkgs/130_frontend/trace-lab-ui` | React explorer, monitor, layouts, charts and recorded fixtures |

### Public API and Import Surfaces

`GET /demo/trace` returns a bounded 750-event snapshot. `POST /demo/run` runs the real clients and returns a summary. The collector accepts batches at `POST /internal/trace/batches`.

`GET /api/correlations` returns evidence for the recent correlation index or an exact typed lookup using `id` and `id_type`. The correlation waterfall groups records by their reported identities and labels coverage and timing separately. `GET /api/timeline` remains the paginated event feed for the event explorer and accepts `correlation_id`, `limit` (1–250), and `before` (the prior page's `next_before`).

### Entry Points

<!-- readme-standards:begin entry-points -->
- `console_scripts` → `notes-pilot` → `trace_lab_demo.notes_pilot:cli`
- `console_scripts` → `tigrbl-trace-lab-demo` → `trace_lab_demo.run:main`
<!-- readme-standards:end entry-points -->

### Injected Dependencies

The demo uses a temporary SQLite database. The collector uses a separate PostgreSQL database. Both serve the same built Vite bundle.

### Protocol Consumers

The scenario uses Python clients for REST, HTTP JSON-RPC, WebSocket JSON-RPC and WebTransport. The React explorer and the exporter use HTTP endpoints.

### Extensions

The adapter preserves typed identifiers and maps native event names for the frontend. Coordinate additions to the response schema with the frontend adapter and tests.

---

## Operations and Readiness

### Operational Requirements

The scenario binds TCP and QUIC to loopback and uses a temporary QUIC certificate. To enforce a retention window, schedule a database job that deletes old rows by the indexed `ingested_at` column. This example retains 14 days of ingested events.

```sql
DELETE FROM timeline_events
WHERE ingested_at < to_char(
  (now() AT TIME ZONE 'UTC') - interval '14 days',
  'YYYY-MM-DD"T"HH24:MI:SS.US'
) || '+00:00';
```

### Health and Observability

The demo snapshot reports its capture revision and the last scenario status. Exporter logs and counters show failures and drops. Ingested events remain readable while the producing app is offline.

### Security and Resource Limits

The collector uses a bearer token for batch ingestion and HTTP Basic credentials for the monitor. Serve remote deployments over HTTPS. The exporter queue is bounded and held in worker memory.

### Compatibility

The uv lock supplies dependencies. The source bootstrap retrieves the pinned public Tigrcorn server, WebTransport probe, and ASGI contract used by the scenario. The CLI accepts `--tigrcorn-source` and `--contract-source` overrides.

---

## Verification

### Tests

```sh
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run ssot validate .
uv run readme-standards check --root . --all
pnpm --filter @tigrbl/trace-lab-ui lint
pnpm --filter @tigrbl/trace-lab-ui build
uv run --locked --package tigrbl-trace-lab-demo tigrbl-trace-lab-demo --port 0 --smoke
```

The smoke test verifies all four transports, WebTransport session grouping, a broker delivery, a committed transaction, and the built frontend's assets and Distributions route.

With the frontend built, set `TRACE_TEST_POSTGRES_URL` to a disposable PostgreSQL database and run `uv run pytest -q` to verify the primary exporter and collector as separate Tigrcorn processes, including replay, collector outage, and persisted history after restart.

### Certification Status

The demo and trace collector are development tooling. The workspace has no certification claim.

### Evidence

The [verification workflow](.github/workflows/verify.yml) runs the package tests and transport smoke check. The [SSOT registry](.ssot/registry.json) records implementation and test evidence.

---

## FAQ

### Why

The monitor keeps a request's transport, invocation, and transaction identities together for drill-down.

### How

Build the shared frontend once and start the demo or collector using the corresponding CLI mode.

### When

Run the PostgreSQL integration test when changing the collector's schema, authentication, or exporter retry behavior.

---

## Documentation and Related Packages

### More Documentation

The [backend guide](pkgs/110_backend/trace-lab-server/README.md) describes the command, endpoints, and exporter import.

### Related Packages

The [UI guide](pkgs/130_frontend/trace-lab-ui/README.md) describes the React explorer and monitor.

### Project Links

<!-- readme-standards:begin project-links -->
- [pypi: tigrbl-trace-lab-demo](https://pypi.org/project/tigrbl-trace-lab-demo/)
<!-- readme-standards:end project-links -->

---

## Contributing

### How to Contribute

Keep trace contract changes paired with tests for the producer and collector paths they affect.

### Development Setup

Run Quick Start from the repository root. It installs the locked uv and pnpm workspaces, builds the UI, and fetches the pinned public WebTransport probe when needed.

### Notes for Maintainers

Regenerate the managed README blocks after editing their manifest declarations or source-linked examples.

---

## Governance

### Ownership and Decision Making

`index.toml` declares the layers and dependency direction. The Tigrbl organization maintains the workspace.

### Standards and Policies

Readme-standards checks the workspace and Python package guides. The SSOT registry tracks the workspace's declared behavior and evidence.

### Lifecycle and Migration

Keep persisted event schemas compatible with existing rows when changing the collector. Rerun the transport smoke and monitor integration checks after updating an upstream source pin.

---

## License and Attribution

### License

<!-- readme-standards:begin license -->
Licensed under `Apache-2.0`. See [LICENSE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/LICENSE).
<!-- readme-standards:end license -->

### Notices

<!-- readme-standards:begin notices -->
See [NOTICE](https://github.com/tigrbl/tigrbl/blob/master/pkgs/170_examples/trace-lab-demo/NOTICE) for attribution.
<!-- readme-standards:end notices -->
