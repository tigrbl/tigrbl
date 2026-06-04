# Runtime Frame Codec SSOT Proposal

This temporary note captures the proposed SSOT scope for implementing a runtime
framing layer with frame codec variants corresponding to Tigrbl's explicit
first-class frames.

The identifiers below are proposal slugs or existing SSOT IDs. New IDs are not
registered until created through the SSOT registry.

## Proposal Scope

The framing layer should be a runtime codec subsystem, not a new transport
layer. Binding specs and kernel plans own legality. Runtime codecs own only
encode/decode behavior for governed frame shapes.

Core rules:

- One codec per frame representation.
- One policy table per binding or lane.
- One compiled plan per operation.
- `jsonrpc`, `json`, `ndjson`, `text`, `bytes`, and `binary` are distinct.
- WebTransport outer framing remains `webtransport`; app-level payload framing
  is lane-scoped through `inner_framing`.
- Unsupported combinations fail closed before runtime dispatch.

## Proposed ADRs

### Reuse Or Update

| ADR | Scope |
|---|---|
| `adr:1133` | App-Level Framing Support Policy |
| `adr:1131` | WebSocket Binding Framing and Subprotocol Policy |
| `adr:1096` | WebTransport Session, Stream, and Datagram Runtime Boundary |
| `adr:1120` | Byte-Oriented Runtime Execution Principles |
| `adr:1006` | Protocol Binding Model |

### Add

| ADR | Decision | Required content |
|---|---|---|
| `adr:1138-runtime-frame-codec-registry-and-frame-envelope-policy` | Runtime framing is a codec registry over first-class frame envelopes. | Define `Frame`, `FrameContext`, codec registry authority, legality separation, WebTransport outer/inner framing split, and fail-closed runtime errors. |

## Proposed SPECs

### Reuse Or Update

| SPEC | Scope |
|---|---|
| `spc:2157` | App-Level Framing Support Matrix Contract |
| `spc:2154` | WebTransport Inner App Framing Contract |
| `spc:2153` | WebSocket Binding Framing and Subprotocol Contract |
| `spc:2155` | Contract Event Classification Consumption Contract |
| `spc:2156` | Contract To KernelPlan Alias Matrix |
| `spc:2107` | WebSocket and WSS Atom Chain Contract |
| `spc:2108` | WebTransport Atom Chain Contract |

### Add

| SPEC | Scope | Required content |
|---|---|---|
| `spc:2168-runtime-frame-codec-registry-contract` | Runtime codec registry, first-class frame model, and codec behavior. | `Frame`, `FrameContext`, `FrameCodec`, registry lookup, encode/decode semantics, codec names, media/content metadata, error behavior, and WebTransport inner codec dispatch. |

## Proposed Features

### Reuse Existing Features

| Feature | Scope |
|---|---|
| `feat:app-level-framing-support-matrix-001` | Govern intended app-level framing support by binding profile, family, exchange, and framing. |
| `feat:app-level-framing-runtime-gating-001` | Require binding legality, codec support, docs projection, and tests before claiming runtime support. |
| `feat:wsbindingspec-framing-001` | WebSocket post-handshake framing declaration. |
| `feat:wsbindingspec-framing-subprotocol-validation-001` | WebSocket framing and subprotocol compatibility validation. |
| `feat:ws-jsonrpc-subprotocol-parity-001` | WS/WSS JSON-RPC parity and subprotocol validation. |
| `feat:ws-ndjson-fail-closed-001` | WS/WSS NDJSON remains explicit and fail closed until supported. |
| `feat:webtransport-inner-framing-lane-boundary-001` | Separate WebTransport outer framing from lane-local inner app framing. |
| `feat:webtransport-stream-framing-runtime-gating-001` | Gate WebTransport stream inner app framing by lane legality and codec support. |
| `feat:webtransport-datagram-framing-runtime-gating-001` | Gate WebTransport datagram inner app framing and reject stream-only codecs. |
| `feat:webtransport-message-lane-rejection-001` | Reject message as a native WebTransport lane. |
| `feat:app-framed-message-codec-runtime-001` | Existing app-framed message codec runtime target. |

### Add Implementation Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:runtime-frame-envelope-001` | Add first-class runtime `Frame` and `FrameContext` models. | Add `tigrbl_runtime.protocol.frames` with stable frame kinds and metadata fields. |
| `feat:runtime-frame-codec-registry-001` | Replace runtime string-switch framing dispatch with registered codecs. | Add a codec registry with explicit lookup and fail-closed unknown-codec behavior. |
| `feat:runtime-json-ndjson-text-bytes-codecs-001` | Implement core JSON, NDJSON, text, bytes, and binary codec variants. | Preserve byte/text/binary distinctions and newline record boundaries. |
| `feat:runtime-jsonrpc-codec-strictness-001` | Keep JSON-RPC as strict JSON-RPC 2.0 document framing. | Reject JSON, NDJSON, or partial JSON-RPC substitutes. |
| `feat:runtime-sse-and-websocket-frame-codecs-001` | Move SSE and WebSocket text behavior into codec objects. | Preserve existing ASGI websocket send adapter output. |
| `feat:webtransport-inner-codec-dispatch-001` | Select lane-local codecs for WebTransport stream/datagram payloads. | Use `inner_framing` only after lane legality validation. |

## Proposed Runtime Frame Model

| Field | Purpose |
|---|---|
| `kind` | First-class runtime frame kind such as `request`, `response`, `message`, `stream_chunk`, `stream_close`, `sse_event`, `websocket_message`, `webtransport_session`, `webtransport_stream_chunk`, or `webtransport_datagram`. |
| `payload` | Decoded application payload or raw bytes/text when the codec is pass-through. |
| `framing` | App-level framing token used for the payload. |
| `content_type` | Declared media/content type when available. |
| `headers` | Optional frame-level headers or metadata. |
| `id` | Request/message/event id when present. |
| `method` | JSON-RPC or operation method selector when present. |
| `lane` | WebTransport lane such as `session`, `bidi_stream`, `unidi_client_stream`, `unidi_server_stream`, or `datagram`. |
| `session_id` | Runtime session identity when present. |
| `stream_id` | Runtime stream identity when present. |
| `datagram_id` | Runtime datagram identity when present. |

## Proposed Codec Variants

| Codec | Behavior | Notes |
|---|---|---|
| `json` | Encode/decode one JSON document. | Does not imply JSON-RPC semantics. |
| `jsonrpc` | Encode/decode strict JSON-RPC 2.0 documents. | Requires JSON-RPC envelope validation. |
| `ndjson` | Encode/decode newline-delimited JSON records. | Does not imply JSON-RPC semantics. |
| `text` | UTF-8 text payload. | Reject invalid UTF-8 on decode. |
| `bytes` | Raw byte payload. | No media semantics. |
| `binary` | Declared binary payload. | Requires explicit binary media/framing contract. |
| `sse` | Encode SSE event frames. | Runtime decode can remain unsupported unless needed. |
| `websocket.text` | Adapt WebSocket text frames to ASGI messages. | Keeps existing websocket adapter behavior. |
| `webtransport` | Represent outer WebTransport session/lane envelope. | Delegates lane payloads to `inner_framing` codecs. |

## T0 Tests

T0 proves static declarations, registry shape, and fail-closed policy. It should
not require runtime I/O.

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:runtime-frame-codec-registry-static-t0` | Every governed codec token has an explicit registry entry or explicit unsupported marker. | A supported framing token is present in policy but absent from the registry. |
| `tst:runtime-frame-envelope-schema-static-t0` | `Frame.kind`, payload, ids, lane metadata, and content metadata are stable. | Frame envelope fields drift or collapse lane/id metadata. |
| `tst:framing-support-matrix-codec-coverage-t0` | `APP_LEVEL_FRAMING_SUPPORT` and `WEBTRANSPORT_INNER_FRAMING_SUPPORT` map to registry coverage. | Policy declares runtime support without codec coverage. |
| `tst:jsonrpc-ndjson-distinction-static-t0` | `jsonrpc`, `json`, `ndjson`, and future `ndjson-jsonrpc` are not aliases. | NDJSON is treated as a JSON-RPC substitute. |
| `tst:webtransport-inner-codec-legality-static-t0` | Session has no inner framing, stream lanes allow stream-safe codecs, datagram excludes `jsonrpc` and `ndjson`. | WebTransport session carries app framing or datagram accepts stream-only framing. |

## T1 Tests

T1 proves direct deterministic runtime codec behavior with unit cases.

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:runtime-json-codec-roundtrip-t1` | JSON document frame encodes and decodes deterministically. | Malformed JSON is silently accepted. |
| `tst:runtime-jsonrpc-codec-strict-validation-t1` | Valid JSON-RPC 2.0 document is accepted. | Missing `jsonrpc: "2.0"` or missing `method` is accepted. |
| `tst:runtime-ndjson-codec-record-boundary-t1` | Newline-delimited JSON records decode by record boundary. | Partial or malformed records are treated as complete frames. |
| `tst:runtime-text-bytes-binary-codec-t1` | UTF-8 text, raw bytes, and declared binary behavior remain distinct. | Bytes/text/binary are collapsed into one generic codec. |
| `tst:runtime-sse-codec-event-format-t1` | `event`, `id`, `retry`, and `data` encode to an SSE event block. | SSE is accepted as generic JSON framing. |
| `tst:runtime-websocket-text-codec-adapter-t1` | WebSocket text codec produces ASGI websocket send messages and decodes text safely. | Invalid UTF-8 or non-text payload silently passes. |
| `tst:webtransport-inner-codec-dispatch-t1` | Lane plus `inner_framing` selects the correct codec. | Illegal lane/framing combinations fall back to a default codec. |

## T2 Tests

T2 proves integration across binding policy, kernel plan, runtime codec dispatch,
and negative behavior.

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:binding-policy-to-codec-runtime-integration-t2` | BindingSpec to kernel plan to codec registry lookup agrees for supported rows. | Kernel plan claims a framing that runtime cannot resolve. |
| `tst:framing-negative-corpus-runtime-t2` | Invalid combinations fail closed: REST+`jsonrpc`, JSON-RPC+`ndjson`, SSE+`json`, WS+`ndjson`, WT outer+`jsonrpc`. | Invalid combinations reach handler/runtime dispatch. |
| `tst:websocket-jsonrpc-subprotocol-codec-t2` | WS/WSS `framing=jsonrpc` requires `jsonrpc` subprotocol and dispatches strict JSON-RPC codec. | WS JSON-RPC runs without subprotocol gating. |
| `tst:webtransport-stream-inner-codec-runtime-t2` | WebTransport stream lanes route `json`, `jsonrpc`, `ndjson`, `text`, `bytes`, and `binary` through inner codec dispatch. | Stream lane ignores `inner_framing` or accepts unknown codecs. |
| `tst:webtransport-datagram-inner-codec-runtime-t2` | WebTransport datagram accepts datagram-safe codecs and rejects `jsonrpc` and `ndjson`. | Datagram dispatch accepts stream-only JSON-RPC or NDJSON framing. |
| `tst:transport-demo-frame-codec-matrix-t2` | Transport demo matrix proves real route behavior for codec-supported rows. | Demo reports unsupported or fail-closed rows as supported. |
| `tst:codec-errors-map-to-runtime-fail-closed-t2` | Malformed payloads produce controlled runtime errors. | Codec failures silently fall back or bypass transport policy. |

## Proposed Entity Matrix

| Layer | Reuse | Add |
|---|---|---|
| ADR | `adr:1133`, `adr:1131`, `adr:1096`, `adr:1120`, `adr:1006` | `adr:1138-runtime-frame-codec-registry-and-frame-envelope-policy` |
| SPEC | `spc:2157`, `spc:2154`, `spc:2153`, `spc:2155`, `spc:2156`, `spc:2107`, `spc:2108` | `spc:2168-runtime-frame-codec-registry-contract` |
| Feature | Existing framing, WebSocket, WebTransport, and app-framed message codec rows | Runtime frame envelope, codec registry, core codecs, strict JSON-RPC codec, SSE/WebSocket codecs, WebTransport inner codec dispatch |
| Tests | Existing T0/T1/T2 classification, WebSocket, and WebTransport tests | New codec registry, envelope, codec roundtrip, negative corpus, and demo matrix tests |

## Proposed Priority Order

| Priority | Work | Reason |
|---|---|---|
| P0 | `adr:1138` and `spc:2168` | Establish the runtime codec registry and frame envelope as the governed implementation boundary. |
| P0 | `feat:runtime-frame-envelope-001` and `feat:runtime-frame-codec-registry-001` | Prevent more string-switch framing logic from accumulating. |
| P0 | T0 registry and matrix coverage tests | Ensure declared support cannot outrun codec coverage. |
| P1 | Core JSON, JSON-RPC, NDJSON, text, bytes, and binary codecs | Close the main app-level codec variants. |
| P1 | T1 codec behavior tests | Prove deterministic direct codec behavior before transport integration. |
| P2 | WebSocket, SSE, and WebTransport inner codec dispatch | Connect codec registry to current transport surfaces. |
| P2 | T2 integration and negative corpus tests | Prove policy, kernel plan, and runtime behavior agree. |
| P3 | Transport demo matrix extension | Turn codec support into user-visible route/demo proof without overstating unsupported rows. |
