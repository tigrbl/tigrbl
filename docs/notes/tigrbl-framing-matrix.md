# Tigrbl Current Framing Support Matrix

Saved from live repo review on 2026-05-23.

This note reflects current support found in the live checkout. It is intentionally
grounded in spec, kernel, runtime, and test surfaces rather than aspirational
framing vocabulary.

## Emoji Legend

- `🟢` supported
- `🟡` partial or constrained
- `🟠` provisional or tracked
- `🔴` not supported or fail-closed

## Current Support Matrix

| Proto | Binding | Default framing | Current support | Notes |
|---|---|---|---|---|
| `http.rest` | `HttpRestBindingSpec` | `json` | `🟢 json` | REST currently rejects non-`json` framing. |
| `https.rest` | `HttpRestBindingSpec` | `json` | `🟢 json` | Same behavior as `http.rest`. |
| `http.jsonrpc` | `HttpJsonRpcBindingSpec` | `jsonrpc` | `🟢 jsonrpc` | Explicit JSON-RPC binding plus runtime encode/decode support. |
| `https.jsonrpc` | `HttpJsonRpcBindingSpec` | `jsonrpc` | `🟢 jsonrpc` | Same behavior as `http.jsonrpc`. |
| `http.stream` | `HttpStreamBindingSpec` | `stream` | `🟢 stream` | First-class HTTP streaming binding. |
| `https.stream` | `HttpStreamBindingSpec` | `stream` | `🟢 stream` | Same behavior as `http.stream`. |
| `http.sse` | `SseBindingSpec` | `sse` | `🟢 sse` | First-class SSE surface with encoder support. |
| `https.sse` | `SseBindingSpec` | `sse` | `🟢 sse` | Same behavior as `http.sse`. |
| `ws` | `WsBindingSpec` | `text` | `🟢 text`, `🟡 jsonrpc`, `🟡 binary/bytes raw`, `🔴 ndjson` | `jsonrpc` requires the `jsonrpc` subprotocol; `ndjson` is explicitly fail-closed. |
| `wss` | `WsBindingSpec` | `text` | `🟢 text`, `🟡 jsonrpc`, `🟡 binary/bytes raw`, `🔴 ndjson` | Same behavior as `ws`, with secure-scope support. |
| `webtransport` | `WebTransportBindingSpec` | `webtransport` | `🟠 transport/session only` | Present in binding, kernel, and event-model surfaces, but still provisional. |
| arbitrary `str` | `MessageBindingSpec` | `bytes` | `🟡 declared` | Declared at spec level; first-class runtime framing support was not established in this review. |
| arbitrary `str` | `DatagramBindingSpec` | `bytes` | `🟡 declared`, `🟠 webtransport-aligned` | Declared at spec level; strongest concrete evidence is under WebTransport event coverage. |

## Important Distinction

The framing token vocabulary is broader than actual implemented support. The spec
declares `json`, `jsonrpc`, `ndjson`, `sse`, `stream`, `text`, `binary`,
`bytes`, and `webtransport`, but the runtime framing atoms reviewed here
explicitly implement only:

- `json`
- `jsonrpc`
- `sse`
- `websocket.text`

That means token presence in the type surface should not be treated as evidence
that the corresponding transport framing is fully implemented.

## Key Repo Signals

- `HttpRestBindingSpec` defaults to `json`.
- `HttpJsonRpcBindingSpec` defaults to `jsonrpc`.
- `HttpStreamBindingSpec` defaults to `stream`.
- `SseBindingSpec` defaults to `sse`.
- `WsBindingSpec` defaults to `text`.
- `WsBindingSpec framing="jsonrpc"` requires the `jsonrpc` subprotocol.
- `WsBindingSpec framing="ndjson"` is planned but not implemented and fails closed.
- `WebTransportBindingSpec` exists, but repo docs and tests still place it in a provisional bucket rather than a fully mature current-target surface.

## File Pointers

- `pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/protocol_bindings.py`
- `pkgs/core/tigrbl_runtime/tigrbl_runtime/protocol/framing_atoms.py`
- `pkgs/core/tigrbl_core/tests/test_canonical_appspec_transport_contract.py`
- `pkgs/core/tigrbl_tests/tests/unit/runtime/test_websocket_atom_chain_contract.py`
- `pkgs/core/tigrbl_tests/tests/unit/runtime/test_webtransport_transport_events_contract.py`
- `docs/developer/operator/websockets-and-sse.md`
- `docs/monitoring-and-transport-support-matrix.md`
