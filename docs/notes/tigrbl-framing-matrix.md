# Tigrbl Current Framing Support Matrix

Saved from live repo review on 2026-06-17.

Reader-facing transport, stream, and framing guidance now lives in
`docs/developer/TRANSPORTS_AND_FRAMING.md`. This note remains as the dated
framing review that fed that consolidated document.

This note reflects current support found in the live checkout. It is intentionally
grounded in spec, kernel, runtime, and test surfaces rather than aspirational
framing vocabulary.

## Legend

- `supported` means policy and executable encode/decode coverage exist.
- `partial` means policy exists but the transport surface is constrained or output-only.
- `provisional` means vocabulary or event modeling exists but mature serving support is not claimed.
- `not supported` means the combination still fails closed.

## Current Support Matrix

| Proto | Binding | Default framing | Current support | Notes |
|---|---|---|---|---|
| `http.rest` | `HttpRestBindingSpec` | `json` | `supported: json` | REST currently rejects non-`json` framing. |
| `https.rest` | `HttpRestBindingSpec` | `json` | `supported: json` | Same behavior as `http.rest`. |
| `http.jsonrpc` | `HttpJsonRpcBindingSpec` | `jsonrpc` | `supported: jsonrpc` | Explicit JSON-RPC binding plus runtime encode/decode support for request, response, error, and batch documents. |
| `https.jsonrpc` | `HttpJsonRpcBindingSpec` | `jsonrpc` | `supported: jsonrpc` | Same behavior as `http.jsonrpc`. |
| `http.stream` | `HttpStreamBindingSpec` | `stream` | `supported: stream`, `bytes`, `binary`, `text`, `json`, `ndjson` | First-class HTTP streaming binding with executable codec atoms. |
| `https.stream` | `HttpStreamBindingSpec` | `stream` | `supported: stream`, `bytes`, `binary`, `text`, `json`, `ndjson` | Same behavior as `http.stream`. |
| `http.sse` | `SseBindingSpec` | `sse` | `partial: sse encode-only` | First-class SSE surface with encoder support. |
| `https.sse` | `SseBindingSpec` | `sse` | `partial: sse encode-only` | Same behavior as `http.sse`. |
| `ws` | `WsBindingSpec` | `text` | `supported: text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson` | `jsonrpc` requires the `jsonrpc` subprotocol; `ndjson` requires the `ndjson` subprotocol. |
| `wss` | `WsBindingSpec` | `text` | `supported: text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson` | Same behavior as `ws`, with secure-scope support. |
| `webtransport` | `WebTransportBindingSpec` | `webtransport` | `partial: lane-validated inner codecs` | Inner stream lanes support `bytes`, `binary`, `text`, `json`, `jsonrpc`, and `ndjson`; datagrams support `bytes`, `binary`, `text`, and `json`. The serving boundary remains provisional. |
| arbitrary `str` | `MessageBindingSpec` | `bytes` | `provisional: declared` | Declared at spec level; strongest concrete evidence is still WebSocket message and WebTransport event coverage. |
| arbitrary `str` | `DatagramBindingSpec` | `bytes` | `partial: WebTransport-aligned` | WebTransport datagram inner codecs execute for `bytes`, `binary`, `text`, and `json`; `jsonrpc` and `ndjson` remain excluded. |

## Important Distinction

The framing token vocabulary is broader than actual transport maturity. The spec
declares `json`, `jsonrpc`, `ndjson`, `sse`, `stream`, `text`, `binary`,
`bytes`, and `webtransport`. Runtime codec atoms now explicitly implement:

- `json`
- `jsonrpc` request, response, error, and batch documents
- `ndjson`
- `text`
- `bytes`
- `binary`
- `stream`
- `sse` encode-only
- `websocket.text`
- `websocket.json`
- `websocket.jsonrpc`
- `websocket.ndjson`
- `websocket.bytes`
- `websocket.binary`
- WebTransport inner encode/decode helpers after lane legality validation

Token presence in a type surface is still not enough by itself. A framing is
runtime-supported only when binding policy and executable codec tests both cover
it.

## Key Repo Signals

- `HttpRestBindingSpec` defaults to `json`.
- `HttpJsonRpcBindingSpec` defaults to `jsonrpc`.
- `HttpStreamBindingSpec` defaults to `stream`.
- `SseBindingSpec` defaults to `sse`.
- `WsBindingSpec` defaults to `text`.
- `WsBindingSpec framing="jsonrpc"` requires the `jsonrpc` subprotocol.
- `WsBindingSpec framing="ndjson"` requires the `ndjson` subprotocol.
- `WebTransportBindingSpec` validates lane-local inner framing before runtime codec dispatch.
- Remaining gaps: REST non-JSON request/response framing, HTTP client-stream exchange split, distinct `wt`/`wts` alias rows, and mature WebTransport serving support.

## File Pointers

- `pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py`
- `pkgs/core/tigrbl_kernel/tigrbl_kernel/protocol_bindings.py`
- `pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/framing/codec.py`
- `pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/framing/app_frame.py`
- `pkgs/core/tigrbl_core/tests/test_canonical_appspec_transport_contract.py`
- `pkgs/core/tigrbl_tests/tests/unit/runtime/test_runtime_frame_codec_contract.py`
- `pkgs/core/tigrbl_tests/tests/unit/runtime/test_websocket_framing_runtime_contract.py`
- `pkgs/core/tigrbl_tests/tests/unit/runtime/test_webtransport_lane_framing_policy.py`
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
| `ws` | `message` | `duplex` | `text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson`; `jsonrpc` and `ndjson` require explicit subprotocol/contract gating |
| `wss` | `message` | `duplex` | `text`, `bytes`, `binary`, `json`, `jsonrpc`, `ndjson`; `jsonrpc` and `ndjson` require explicit subprotocol/contract gating |
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
