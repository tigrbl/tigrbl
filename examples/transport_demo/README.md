# Tigrbl Transport Demo Bundle

This bundle collects the transport demos requested for the current checkout into one runnable app:

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

The app entrypoint is [app.py](/E:/swarmauri_github/tigrbl/examples/transport_demo/app.py:1).

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
python -m tigrbl serve .\examples\transport_demo\app.py:build_app --server uvicorn --host 127.0.0.1 --port 8000
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
python -m tigrbl serve .\examples\transport_demo\app.py:build_app --server uvicorn --deployment-profile strict-h1-origin --proxy-contract strict --early-data-policy reject
```

### `h2`

```powershell
python -m tigrbl serve .\examples\transport_demo\app.py:build_app --server hypercorn --deployment-profile strict-h2-origin --proxy-contract strict --early-data-policy reject --http2-max-concurrent-streams 128 --http2-initial-window-size 65535
```

### `h3 / quic`

```powershell
python -m tigrbl serve .\examples\transport_demo\app.py:build_app --server tigrcorn --deployment-profile strict-h3-edge --proxy-contract edge-normalized --early-data-policy edge-replay-guarded --quic-metrics connections,handshake,retry,migration
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
