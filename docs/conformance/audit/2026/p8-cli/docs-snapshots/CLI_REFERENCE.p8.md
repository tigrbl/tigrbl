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

### Flag defaults

- `--server`: `uvicorn`
- `--host`: `127.0.0.1`
- `--port`: `8000`
- `--workers`: `1`
- `--docs-path`: `/docs`
- `--openapi-path`: `/openapi.json`
- `--openrpc-path`: `/openrpc.json`
- `--lens-path`: `/lens`

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

## Notes on smoke coverage

The current checkpoint verifies the CLI at two levels:

1. command smoke via `python -m tigrbl ...` for the non-blocking commands
2. supported-server runner smoke via monkeypatched dispatch/argument translation tests for Uvicorn, Hypercorn, Gunicorn, and Tigrcorn

Installed-package and live-network server smoke remains part of the later evidence/reproducibility gates.
