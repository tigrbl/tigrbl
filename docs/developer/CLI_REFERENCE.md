# CLI Reference

## Purpose

The `tigrbl` command is the unified framework CLI for the current cycle.

## App target syntax

Commands that operate on an application accept either:

- `<module:attr>`
- `<path.py:attr>`

Examples:

- `tigrbl routes mypkg.api:app`
- `tigrbl openapi ./examples/my_app.py:app`
- `tigrbl dev ./examples/my_app.py:build_app`

If the resolved target is a zero-argument factory, the CLI calls it. If the resolved target is a `TigrblRouter`, the CLI wraps it in a `TigrblApp` for serving and inspection.

## Commands

### `tigrbl run`

Serve a Tigrbl app with the selected server runner.

### `tigrbl serve`

Serve a Tigrbl app with the selected server runner.

### `tigrbl dev`

Serve a Tigrbl app in development mode. If `--reload` is not supplied explicitly, this command enables reload by default.

### `tigrbl routes`

Print the current HTTP, WebSocket, and static-mount route inventory.

### `tigrbl openapi`

Print the OpenAPI document for the target app as JSON.

### `tigrbl openrpc`

Print the OpenRPC document for the target app as JSON.

### `tigrbl doctor`

Print a JSON diagnostic summary covering:

- target resolution
- app type / title / version
- route counts
- docs paths
- engine capabilities when available
- supported server availability
- known engine kinds

### `tigrbl capabilities`

Print a JSON summary covering:

- the CLI command set
- the governed flag set
- supported server availability
- known engine kinds
- optional app-specific diagnostic data when an app target is supplied

## Required flags

The unified CLI exposes these governed flags:

- `--server {tigrcorn,uvicorn,hypercorn,gunicorn}`
- `--host`
- `--port`
- `--reload`
- `--workers`
- `--root-path`
- `--proxy-headers`
- `--uds`
- `--docs-path`
- `--openapi-path`
- `--openrpc-path`
- `--lens-path`
- `--statsd-addr`
- `--dogstatsd-tags`
- `--otel-endpoint`
- `--trace-sample-rate`
- `--drain-timeout`
- `--shutdown-timeout`
- `--concurrency-limit`
- `--admission-queue`
- `--backlog`
- `--ws-heartbeat`
- `--ws-heartbeat-timeout`
- `--http2-max-concurrent-streams`
- `--http2-initial-window-size`
- `--http3-max-data`
- `--http3-max-uni-streams`
- `--alpn-policy`
- `--ocsp-policy`
- `--revocation-policy`
- `--interop-bundle-dir`
- `--benchmark-bundle-dir`
- `--deployment-profile`
- `--proxy-contract`
- `--early-data-policy`
- `--origin-static-policy`
- `--quic-metrics`
- `--qlog-dir`

### Flag defaults

- `--server`: `uvicorn`
- `--host`: `127.0.0.1`
- `--port`: `8000`
- `--workers`: `1`
- `--docs-path`: `/docs`
- `--openapi-path`: `/openapi.json`
- `--openrpc-path`: `/openrpc.json`
- `--lens-path`: `/lens`
- `--trace-sample-rate`: `1.0`
- `--drain-timeout`: `30.0`
- `--shutdown-timeout`: `30.0`
- `--admission-queue`: `1024`
- `--backlog`: `2048`
- `--ws-heartbeat`: `30.0`
- `--ws-heartbeat-timeout`: `30.0`
- `--http2-max-concurrent-streams`: `128`
- `--http2-initial-window-size`: `65535`
- `--http3-max-data`: `1048576`
- `--http3-max-uni-streams`: `128`
- `--alpn-policy`: `h3,h2,http/1.1`
- `--ocsp-policy`: `optional`
- `--revocation-policy`: `best_effort`
- `--proxy-contract`: `strict`
- `--early-data-policy`: `reject`
- `--origin-static-policy`: `strict`
- `--quic-metrics`: `connections,handshake,retry,migration`

## Supported serving paths

### Uvicorn

- available through the base package dependency set
- executed in-process by the CLI runner

### Hypercorn

- optional server dependency
- executed in-process by the CLI runner when installed

### Gunicorn

- optional server dependency
- executed through a Gunicorn application wrapper using `uvicorn.workers.UvicornWorker`

### Tigrcorn

- optional server dependency
- executed through the installed `tigrcorn` module when it exposes a compatible `run(...)` or `serve(...)` callable
- operator-facing controls are published through the Tigrbl CLI surface and forwarded directly into Tigrcorn-compatible runners

## Tigrcorn operator controls

The current next-target checkpoint publishes the following Tigrcorn-facing controls as public CLI/config surfaces:

- metrics export: `--statsd-addr`, `--dogstatsd-tags`, `--otel-endpoint`, `--trace-sample-rate`
- shutdown and drain: `--drain-timeout`, `--shutdown-timeout`
- admission and backlog: `--concurrency-limit`, `--admission-queue`, `--backlog`
- WebSocket liveness: `--ws-heartbeat`, `--ws-heartbeat-timeout`
- HTTP/2 flow control: `--http2-max-concurrent-streams`, `--http2-initial-window-size`
- HTTP/3 / QUIC runtime tuning: `--http3-max-data`, `--http3-max-uni-streams`
- TLS and negotiation policy: `--alpn-policy`, `--ocsp-policy`, `--revocation-policy`
- release-gated artifact directories: `--interop-bundle-dir`, `--benchmark-bundle-dir`
- blessed deployment profiles: `--deployment-profile`
- normative hardening contracts: `--proxy-contract`, `--early-data-policy`, `--origin-static-policy`
- QUIC observability: stable counters via `--quic-metrics`; qlog-like export via `--qlog-dir` is explicitly experimental

The CLI validates these values before runner dispatch and exposes the resolved operator state through `tigrbl doctor` and `tigrbl capabilities`.

## Tigrcorn hardening profiles

The current Tigrcorn hardening checkpoint publishes five blessed deployment profiles:

- `strict-h1-origin`
- `strict-h2-origin`
- `strict-h3-edge`
- `strict-mtls-origin`
- `static-origin`

Operator pages live under `docs/developer/operator/profiles/`. Machine-readable profile documents, negative corpora, and profile certification reports live under `reports/certification_state/profiles/` and `reports/certification_state/negative_corpora/`.

## Example configs

Repo-owned operator config examples for Tigrcorn live under:

- `docs/developer/examples/tigrcorn/phase5-operator-config.json`
- `docs/developer/examples/tigrcorn/phase5-interop-bundle-manifest.json`
- `docs/developer/examples/tigrcorn/phase5-benchmark-bundle-manifest.json`

## Notes on smoke coverage

The current checkpoint verifies the CLI at two levels:

1. command smoke via `python -m tigrbl ...` for the non-blocking commands
2. supported-server runner smoke via monkeypatched dispatch/argument translation tests for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn

Installed-package, live-network server smoke, and release-grade Tigrcorn interop/benchmark evidence remain part of later evidence/reproducibility gates.
