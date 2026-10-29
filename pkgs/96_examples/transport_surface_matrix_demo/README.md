# Tigrbl Transport Surface Matrix Demo

This UV project collects the transport-surface demos requested for the current checkout into one runnable app:

- `h1.1`, `h2`, `h3/quic`
- `h1.1/h2/h3` with REST
- `h1.1/h2/h3` with JSON-RPC
- `stream`
- `sse`
- `stream ndjson`
- `websocket (ws/wss)`
- `wss + ndjson`
- `wss + jsonrpc`
- `mtls`
- `webtransport (single session with 1 unidirectional stream, 1 bidirectional stream, and datagram messages)`

The app entrypoint is `pkgs/96_examples/transport_surface_matrix_demo/app.py`.

## What Is Runnable Now

| Demo | Path / surface | Repo-grounded status |
|---|---|---|
| REST | `/items`, `/items/{id}` | runnable |
| JSON-RPC | `/rpc` | runnable |
| stream | `/stream/raw` | runnable |
| stream ndjson | `/stream/ndjson` | runnable |
| sse | `/sse/events` | runnable |
| websocket `ws` | `/ws/echo` | runnable |
| websocket `wss` | `/wss/echo` | runnable at app/binding level; needs TLS-capable serving layer |
| `wss + jsonrpc` | `/wss/jsonrpc` | runnable at app/binding level; requires `jsonrpc` subprotocol |
| `wss + ndjson` | fail-closed negative demo | rejected without the required `ndjson` subprotocol |
| mtls | `/mtls/echo` | docs and security-scheme demo are runnable; real client cert exchange depends on serving layer and cert material |
| webtransport session | `/transport/session` | provisional binding demo; the app models the session payload and metadata honestly, but this repo does not yet claim a mature release-grade WebTransport server path |

## Serve The Demo

Run the bundle with the CLI:

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server uvicorn --host 127.0.0.1 --port 8000
```

Available docs surfaces:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/openapi.json`
- `http://127.0.0.1:8000/openrpc.json`
- `http://127.0.0.1:8000/lens`
- `http://127.0.0.1:8000/asyncapi.json`
- `http://127.0.0.1:8000/matrix`

## HTTP Profile Demos

These rows are operator-control demos. The same app is served with different blessed profile settings; actual protocol negotiation depends on the selected server.

### `h1.1`

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server uvicorn --deployment-profile strict-h1-origin --proxy-contract strict --early-data-policy reject
```

### `h2`

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server hypercorn --deployment-profile strict-h2-origin --proxy-contract strict --early-data-policy reject --http2-max-concurrent-streams 128 --http2-initial-window-size 65535
```

### `h3 / quic`

```powershell
uv run --project .\examples\transport_surface_matrix_demo python -m tigrbl serve .\examples\transport_surface_matrix_demo\app.py:build_app --server tigrcorn --deployment-profile strict-h3-edge --proxy-contract edge-normalized --early-data-policy edge-replay-guarded --quic-metrics connections,handshake,retry,migration
```

## Test

```powershell
cd .\examples\transport_surface_matrix_demo
uv run pytest
```

## REST And JSON-RPC Over H1/H2/H3

REST demo calls:

```powershell
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\":\"Ada\"}"
curl http://127.0.0.1:8000/items/1
```

JSON-RPC demo calls:

```powershell
curl -X POST http://127.0.0.1:8000/rpc -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"DemoItem.create\",\"params\":{\"name\":\"Ada\"},\"id\":1}"
curl -X POST http://127.0.0.1:8000/rpc -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"DemoItem.read\",\"params\":{\"id\":1},\"id\":2}"
```

## Websocket Notes

- `ws/wss` text echo uses `/ws/echo` and `/wss/echo`.
- `wss + jsonrpc` uses `/wss/jsonrpc` and requires the `jsonrpc` subprotocol.
- `wss + ndjson` requires the `ndjson` subprotocol. The negative demo intentionally omits that subprotocol so `WsBindingSpec(proto="wss", framing="ndjson")` still raises before runtime dispatch.

## mTLS Notes

For the app-side security scheme and route:

- serve the app with `--deployment-profile strict-mtls-origin --ocsp-policy strict --revocation-policy strict`
- hit `/mtls/echo`

For a client-side SPIFFE/TLS helper example, reuse [exchange_mtls.py](/E:/swarmauri_github/tigrbl/pkgs/apps/tigrbl_spiffe/examples/exchange_mtls.py:1).

## WebTransport Notes

`/transport/session` returns one honest session payload with:

- one unidirectional stream row
- one bidirectional stream row
- one client-to-server datagram and one server-to-client datagram

That matches the requested demo shape while staying honest that current repo support is still provisional at the WebTransport transport boundary.


## What is tigrbl-transport-surface-matrix-demo?

Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

## Why use tigrbl-transport-surface-matrix-demo?

Use this project for tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

## When should I install tigrbl-transport-surface-matrix-demo?

Use it when your application or development task needs the surface described below.
Examples and experimental projects should be run from this checkout.

## Who is tigrbl-transport-surface-matrix-demo for?

Tigrbl maintainers and application developers working with this project’s APIs.

## Where does tigrbl-transport-surface-matrix-demo fit?

Source: `pkgs/96_examples/transport_surface_matrix_demo` in the Tigrbl workspace.

## How does tigrbl-transport-surface-matrix-demo work?

The transport demonstration app in app.py. The examples and implementation above describe the configuration and execution flow.

## Certification Status

No independent release qualification is claimed by this README. Inspect current
repository test results and the applicable release gates before deployment.

## Install

From the repository root:

```console
uv sync --project pkgs/96_examples/transport_surface_matrix_demo
```

## Surface Coverage

| Surface | Value |
| --- | --- |
| Project | `tigrbl-transport-surface-matrix-demo` |
| Python requirement | `>=3.10,<3.15` |
| Python range | 3.10 \| 3.11 \| 3.12 \| 3.13 \| 3.14 |
| Source/import surface | `app.py` |

Supported Python versions: 3.10 | 3.11 | 3.12 | 3.13 | 3.14.

## What It Owns

Tigrbl transport surface matrix example for REST, JSON-RPC, streaming, SSE, WebSocket, mTLS, and WebTransport.

## Public API and Import Surface

The transport demonstration app in app.py. See the project source and existing examples above for supported call signatures.

## Usage Examples

The walkthrough above is retained. The entry surface can be loaded with:

```console
uv run --directory pkgs/96_examples/transport_surface_matrix_demo python -c "import app"
```

## How To Choose This Package

Choose this project when its stated surface matches your task. Examples and
experimental integrations do not imply production support for every transport.

## Related Packages

See [the workspace package catalog](https://github.com/tigrbl/tigrbl/tree/master/pkgs)
and the dependencies in [pyproject.toml](pyproject.toml).

## Documentation Links

- [Tigrbl documentation](https://github.com/tigrbl/tigrbl/tree/master/docs)
- [Project source](https://github.com/tigrbl/tigrbl/tree/master/pkgs/96_examples/transport_surface_matrix_demo)

## Support

Report reproducible issues at [GitHub](https://github.com/tigrbl/tigrbl/issues)
or discuss usage on [Discord](https://discord.gg/K4YTAPapjR).

## License

[Apache 2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

![License](https://img.shields.io/badge/license-Apache%202.0-525252)
