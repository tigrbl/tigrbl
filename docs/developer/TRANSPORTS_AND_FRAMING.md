# Transports and Framing

Tigrbl is a schema-first ASGI framework family with a transport-aware runtime model. It projects one operation inventory into REST, JSON-RPC, HTTP streaming, SSE, WebSocket, and WebTransport-aware runtime planning while keeping protocol, exchange, stream carrier, and application framing separate.

This page is the reader-facing transport and framing map for the current checkout. The normative contracts remain the SSOT registry and authored SPEC rows; this document consolidates them into one practical reference.

For a translation guide comparing these surfaces to ASGI 3, Starlette,
FastAPI, WebSocket, and WebTransport concepts, see
`docs/developer/TRANSPORT_EQUIVALENCE.md`.

## Status Legend

| Status | Meaning |
|---|---|
| Current target | Public support surface in the current target. |
| Active line | Implemented or tracked, but not a frozen current-target claim. |
| Provisional | Modeled or partially implemented; do not present as mature release-grade support. |
| Delegated | Tigrbl consumes or exposes configuration/runtime metadata, but the server or protocol stack owns the wire mechanics. |
| Unsupported | Intentionally rejected or de-scoped. |

## Transport Surface Matrix

| Surface | Tigrbl binding/runtime status | Underlying protocol status | Primary Tigrbl role |
|---|---|---|---|
| REST over HTTP/HTTPS | Current target | Delegated to ASGI server/runtime | Resource-oriented CRUD and HTTP request/response projection. |
| JSON-RPC over HTTP/HTTPS | Current target | Delegated to ASGI server/runtime | Method-oriented RPC projection, batch-capable envelopes, and OpenRPC generation. |
| HTTP request/response streaming | Current target | Delegated to ASGI server/runtime | Client request-body streams and server response-body streams as application stream carriers. |
| SSE / WHATWG event stream | Current target | Delegated HTTP response streaming | Browser-friendly server event streams using `text/event-stream`. |
| WebSocket / WSS text | Current target | Delegated WebSocket upgrade and socket lifecycle | Bidirectional message workflows through runtime channel handling. |
| WebSocket / WSS JSON-RPC | Active line | Delegated WebSocket upgrade and socket lifecycle | JSON-RPC message framing when the required subprotocol is declared. |
| WebTransport session/stream/datagram | Provisional | Delegated HTTP/3/WebTransport serving boundary | Lane-aware session, stream, and datagram modeling with fail-closed validation. |
| HTTP/1.1 wire conformance | Delegated | Server/runtime boundary | Tigrbl models request and response body carriers; it does not claim native h11 stream IDs or multiplexing. |
| HTTP/2 wire conformance | Delegated | Server/runtime boundary | Tigrbl consumes runtime capability metadata; the serving stack owns stream IDs, flow control, HPACK, and connection behavior. |
| HTTP/3 / QUIC wire conformance | Delegated | Server/runtime boundary | Tigrbl separates plain H3 carrier modeling from WebTransport lanes; the serving stack owns QUIC, QPACK, flow control, and TLS termination. |

## Binding Profiles

| Binding class | Protocol token | Profile | Exchange | Default framing | Status |
|---|---|---|---|---|---|
| `HttpRestBindingSpec` | `http.rest`, `https.rest` | `rest` | `request_response` | `json` | Current target |
| `HttpJsonRpcBindingSpec` | `http.jsonrpc`, `https.jsonrpc` | `jsonrpc` | `request_response` | `jsonrpc` | Current target |
| `HttpStreamBindingSpec` | `http.stream`, `https.stream` | `stream` | `server_stream` or `client_stream` | `stream` | Current target |
| `SseBindingSpec` | `http.sse`, `https.sse` | `sse` | `server_stream` | `sse` | Current target |
| `WsBindingSpec` / `WebSocketBindingSpec` | `ws`, `wss` | `websocket` | `bidirectional_stream` | `text` | Current target for text; active line for JSON-RPC and NDJSON framing |
| `WebTransportBindingSpec` | `webtransport` | `session`, `bidi_stream`, `unidi_client_stream`, `unidi_server_stream`, `datagram` | Lane-specific | `webtransport` outer framing | Provisional |
| `MessageBindingSpec` | arbitrary string | generic message family | `fire_and_forget` | `bytes` | Provisional generic declaration |
| `DatagramBindingSpec` | arbitrary string | generic datagram family | `fire_and_forget` | `bytes` | Partial, strongest current evidence is WebTransport-aligned datagram behavior |

## Stream and Carrier Taxonomy

| Carrier / stream row | Initiator | Direction / exchange | Application framing allowed | Status | Notes |
|---|---|---|---|---|---|
| HTTP/1.1 request body | Client | `client_stream` | `bytes`, `binary`, `text`, `json`, `ndjson` | Current target as HTTP streaming | Tigrbl must not claim native h11 stream IDs, multiplexing, or bidirectional transport streams. |
| HTTP/1.1 response body | Server | `server_stream` | `bytes`, `binary`, `text`, `json`, `ndjson`, `stream` | Current target as HTTP streaming | Used for progressive responses and server streaming. |
| HTTP/2 request stream | Client | Request/response carrier; extension-aware bidirectional use requires explicit extension context | Binding-framing dependent | Delegated | Tigrbl does not own HTTP/2 stream ID allocation or flow-control algorithms. |
| HTTP/2 push stream | Server | Response-only push carrier | Binding-framing dependent | Delegated | Not an arbitrary server-initiated bidirectional application stream. |
| HTTP/3 request stream | Client | Bidirectional QUIC request stream carrying one request and its responses | Binding-framing dependent | Delegated | Plain H3 request streams stay separate from WebTransport lanes. |
| HTTP/3 push stream | Server | Server-initiated unidirectional response stream | Binding-framing dependent | Delegated | Not an arbitrary bidirectional application stream. |
| HTTP/3 control stream | Transport stack | Control metadata | No app-level framing | Unsupported for app payloads | Typed transport stream, not an application payload carrier. |
| QPACK encoder/decoder streams | Transport stack | Compression metadata | No app-level framing | Unsupported for app payloads | QPACK is outside Tigrbl framework-owned conformance. |
| HTTP/3 extension stream | Extension-defined | Extension-defined | Requires explicit extension context | Delegated/provisional | Extension streams must name the extension before application framing is allowed. |
| WebTransport session lane | Session | Session lifecycle | No app-level framing | Provisional | Carries session metadata, not application payload frames. |
| WebTransport bidirectional stream | Client or server, explicitly preserved | `bidirectional_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson` | Provisional | Bidirectional rows must preserve stream initiator metadata. |
| WebTransport unidirectional client stream | Client | `client_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson` | Provisional | Client-to-server stream lane. |
| WebTransport unidirectional server stream | Server | `server_stream` | `bytes`, `binary`, `text`, `json`, `jsonrpc`, `ndjson` | Provisional | Server-to-client stream lane. |
| WebTransport datagram | Client or server | Datagram / unordered payload unit | `bytes`, `binary`, `text`, `json` | Provisional | `jsonrpc` and `ndjson` are intentionally excluded for datagrams. |

## Framing Matrix

| Framing | Where it is supported | Status | Rules |
|---|---|---|---|
| `json` | REST, HTTP stream, WebSocket, WebTransport stream lanes, WebTransport datagrams | Current target for REST/stream/WS; provisional for WebTransport | JSON payload framing only; does not imply JSON-RPC semantics. |
| `jsonrpc` | JSON-RPC over HTTP, WebSocket with subprotocol, WebTransport stream lanes | Current target for HTTP JSON-RPC; active line for WebSocket; provisional for WebTransport streams | Strict JSON-RPC 2.0 request, response, error, notification, or batch document framing. |
| `ndjson` | HTTP stream, WebSocket with subprotocol, WebTransport stream lanes | Current target for HTTP stream; active line for WebSocket; provisional for WebTransport streams | Newline-delimited JSON records. Does not imply JSON-RPC. |
| `sse` | SSE bindings only | Current target, encode-oriented | Exclusive to `http.sse` / `https.sse` and `text/event-stream` output. |
| `stream` | HTTP stream bindings | Current target | Generic stream framing for progressive responses and stream-oriented operation output. |
| `text` | WebSocket, HTTP stream, WebTransport stream lanes, WebTransport datagrams | Current target for HTTP stream/WS; provisional for WebTransport | Text payload framing. |
| `bytes` | HTTP stream, WebSocket, WebTransport stream lanes, WebTransport datagrams, generic message/datagram specs | Current target for HTTP stream/WS; provisional or partial elsewhere | Raw byte payload framing. |
| `binary` | HTTP stream, WebSocket, WebTransport stream lanes, WebTransport datagrams | Current target for HTTP stream/WS; provisional for WebTransport | Binary payload with a declared binary media/framing contract. |
| `multipart/form-data` | REST binding policy and codec registry | Active line | Form-data payloads are explicitly framed; unsupported combinations still fail closed. |
| `webtransport` | WebTransport outer binding framing | Provisional | Outer transport framing only. App-level framing lives inside the selected WebTransport lane. |
| `websocket.text` | Runtime codec registry | Current target | WebSocket text message codec. |
| `websocket.json` | Runtime codec registry | Current target | WebSocket JSON message codec. |
| `websocket.jsonrpc` | Runtime codec registry | Active line | Requires JSON-RPC subprotocol/contract gating. |
| `websocket.ndjson` | Runtime codec registry | Active line | Requires NDJSON subprotocol/contract gating. |
| `websocket.bytes` | Runtime codec registry | Current target | WebSocket bytes message codec. |
| `websocket.binary` | Runtime codec registry | Current target | WebSocket binary message codec. |

## Fail-Closed Rules

- `jsonrpc` means complete JSON-RPC document semantics. It is not implied by `json`, `ndjson`, or any stream carrier.
- `ndjson` means newline-delimited JSON records. It is not newline-delimited JSON-RPC unless a future distinct framing token, such as `ndjson-jsonrpc`, is explicitly introduced.
- `sse` is exclusive to SSE bindings.
- WebSocket `jsonrpc` and `ndjson` framing require the matching declared subprotocol or contract gating.
- WebTransport `webtransport` is outer framing only; inner application framing must be valid for the selected lane.
- WebTransport datagrams reject `jsonrpc` and `ndjson`.
- Plain HTTP/3 bindings must not claim WebTransport streams or datagrams.
- H3 control streams and QPACK streams must not be treated as application payload carriers.
- Unsupported transport/framing combinations fail during binding validation, planning, or runtime handling instead of being guessed.

## Ownership Boundary

Tigrbl owns schema-first authoring, binding declarations, operation projection, kernel/runtime planning, lifecycle phases, framing codecs, channel metadata, and fail-closed validation.

The serving/runtime stack owns wire-level HTTP/1.1, HTTP/2, HTTP/3, QUIC, TLS termination, HPACK, QPACK, flow control, ALPN negotiation, and concrete server transport behavior. Tigrbl can expose configuration and consume runtime capability metadata for those layers, but it does not present them as framework-owned conformance claims.

## Source Pointers

- Binding policy and framing allowlists: `pkgs/core/tigrbl_core/tigrbl_core/_spec/binding_spec.py`
- Runtime framing codecs: `pkgs/core/tigrbl_atoms/tigrbl_atoms/atoms/framing/codec.py`
- WebTransport runtime channel state: `pkgs/core/tigrbl_atoms/tigrbl_atoms/runtime_channel.py`
- Plain protocol stream taxonomy: `pkgs/core/tigrbl_kernel/tigrbl_kernel/protocol_streams.py`
- Public support and monitoring boundary: `docs/monitoring-and-transport-support-matrix.md`
- Current target boundary: `docs/conformance/CURRENT_TARGET.md`
- SSOT stream and protocol SPECs: `SPEC-2185`, `SPEC-2186`, `SPEC-2190`, `SPEC-2191`, `SPEC-2192`, and `SPEC-2193`
