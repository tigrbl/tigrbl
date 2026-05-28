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

## Dated Addendum: Intended App-Level Framing Support

Date: 2026-05-27

This addendum records the proposed contract target for app-level framing support.
Each protocol, binding, and lane row owns its framing declaration locally. Secure
variants repeat their framing policy explicitly; TLS, mTLS, ALPN, QUIC, and
HTTP version facts remain scope metadata, not framing shortcuts.

| Protocol / Binding / Lane | Family | Exchange | Explicit app-level framing support |
|---|---|---|---|
| `http.rest` | `request` | `unary` | `json` required; `text`, `bytes`, `binary` allowed for explicitly declared non-JSON endpoints |
| `https.rest` | `request` | `unary` | `json` required; `text`, `bytes`, `binary` allowed for explicitly declared non-JSON endpoints |
| `http.jsonrpc` | `request` | `unary` | `jsonrpc` required and exclusive |
| `https.jsonrpc` | `request` | `unary` | `jsonrpc` required and exclusive |
| `http.stream.request` | `stream` | `client_stream` | `bytes`, `binary`, `text`, `json`, `ndjson` |
| `https.stream.request` | `stream` | `client_stream` | `bytes`, `binary`, `text`, `json`, `ndjson` |
| `http.stream.response` | `stream` | `server_stream` | `bytes`, `binary`, `text`, `json`, `ndjson` |
| `https.stream.response` | `stream` | `server_stream` | `bytes`, `binary`, `text`, `json`, `ndjson` |
| `http.sse` | `stream` | `server_stream` | `sse` required and exclusive |
| `https.sse` | `stream` | `server_stream` | `sse` required and exclusive |
| `ws` | `message` | `duplex` | `text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson`; `jsonrpc` requires explicit subprotocol/contract gating |
| `wss` | `message` | `duplex` | `text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson`; `jsonrpc` requires explicit subprotocol/contract gating |
| `wt.session` | `session` | `unary` | no app-level framing; session metadata only |
| `wts.session` | `session` | `unary` | no app-level framing; session metadata only |
| `wt.bidi_stream` | `stream` | `duplex` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wts.bidi_stream` | `stream` | `duplex` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wt.unidi_client_stream` | `stream` | `client_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wts.unidi_client_stream` | `stream` | `client_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wt.unidi_server_stream` | `stream` | `server_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wts.unidi_server_stream` | `stream` | `server_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson`; stream record-boundary rules required |
| `wt.datagram` | `datagram` | `duplex` | `bytes`, `binary`, `text`, `json`; `jsonrpc` and `ndjson` excluded by default |
| `wts.datagram` | `datagram` | `duplex` | `bytes`, `binary`, `text`, `json`; `jsonrpc` and `ndjson` excluded by default |

### Addendum Rules

- `jsonrpc` means complete JSON-RPC message semantics. It is not implied by
  `json`, `ndjson`, or any stream carrier.
- `ndjson` means newline-delimited JSON records. It does not imply JSON-RPC
  semantics. Newline-delimited JSON-RPC would require a distinct governed
  framing token, such as `ndjson-jsonrpc`.
- `bytes` means raw byte payload.
- `binary` means binary payload with a declared binary media/framing contract.
  It is not automatically identical to `bytes`.
- `sse` is exclusive to SSE.
- For WebTransport, `webtransport` is outer transport framing only. App-level
  framing lives inside the selected lane: bidirectional stream, unidirectional
  stream, or datagram.
