# 11 ASGI Transport Projection

This section proposes the projection contract from ASGI `scope`, `receive`, and
`send` into Tigrbl runtime transport events.

## Purpose

ASGI is the server/app boundary, but it is not the full semantic model. Tigrbl
must project ASGI messages into canonical runtime families such as request,
message, stream, session, and datagram. This keeps server-specific details from
becoming hidden semantic authority while still allowing adapters to use ASGI
metadata safely.

## Proposed ADRs

| ADR | Decision | Why it is needed |
|---|---|---|
| `adr:asgi-is-projection-input-not-semantic-authority` | ASGI messages are projection inputs, not Tigrbl semantic authority. | Prevents server-specific shapes from bypassing kernel/runtime semantics. |
| `adr:tigrbl-runtime-semantics-sit-above-asgi` | Tigrbl semantics are defined above ASGI through explicit projection rules. | Enables portable runtime behavior across ASGI servers and transports. |

## Proposed SPECs

| SPEC | Scope | Required content |
|---|---|---|
| `spc:asgi-scope-projection-contract` | How ASGI `scope` maps to Tigrbl transport metadata. | Scope type, path, headers, client/server data, subprotocols, WebTransport metadata, and normalized ids. |
| `spc:asgi-receive-event-projection` | How ASGI receive events map to runtime events. | HTTP body, WebSocket receive/disconnect, WebTransport stream/datagram/session events, and invalid messages. |
| `spc:asgi-send-event-projection` | How runtime send intent maps to ASGI send events. | Response start/body, WebSocket send/close, stream emits, WebTransport sends, and completion fences. |
| `spc:server-metadata-projection-rules` | Which server-specific metadata can become runtime metadata. | Normalization, allowlist, trace-only metadata, and unsupported metadata handling. |
| `spc:http-body-stream-projection` | HTTP body stream projection by binding kind. | Unary request body, client stream body, chunking, end-of-body, abort, and backpressure behavior. |

## Proposed Features

| Feature | Description | Implementation direction |
|---|---|---|
| `feat:asgi-transport-projection` | Add one governed projection layer from ASGI to Tigrbl events. | Centralize projection helpers and make runtime adapters use them. |
| `feat:websocket-asgi-message-projection` | Project WebSocket ASGI events to message/session events. | Normalize connect, receive, send, close, and disconnect. |
| `feat:webtransport-asgi-message-projection` | Project WebTransport ASGI-like events to session/stream/datagram events. | Normalize session id, stream id, datagram id, lane, and direction metadata. |
| `feat:http-body-stream-projection` | Project HTTP bodies as unary or stream input based on binding. | Add binding-aware HTTP body projection. |
| `feat:server-metadata-normalization` | Govern server metadata admission. | Allowlist canonical fields and route the rest to trace-only metadata. |

## Proposed Tests

| Test | Valid scenario | Invalid scenario |
|---|---|---|
| `tst:websocket-receive-projects-message-received` | ASGI `websocket.receive` becomes `message.received`. | WebSocket receive bypasses runtime event taxonomy. |
| `tst:wt-stream-receive-projects-stream-chunk-received` | WebTransport stream receive becomes `stream.chunk.received` with session/stream ids. | WebTransport stream payload is treated as generic message. |
| `tst:http-body-stream-projects-by-binding-kind` | HTTP body projects to unary request for REST and stream chunks for stream binding. | Stream binding consumes body as one opaque request without policy. |
| `tst:asgi-message-cannot-bypass-kernel-taxonomy` | Unknown ASGI message fails closed or is trace-only. | Unknown ASGI message creates runtime semantic event. |
| `tst:server-specific-metadata-not-canonical-without-rule` | Server metadata is ignored or trace-only unless allowlisted. | Server-specific field becomes canonical state without rule. |

## Invariants

- Tigrbl semantics sit above ASGI.
- ASGI details are inputs to projection, not the semantic contract.
- Unknown or unsupported ASGI messages fail closed or become trace-only.
- Projection must preserve identity fields needed for lifecycle, leakage, trace, and replay.
- Projection must not invent stronger delivery guarantees than the carrier provides.

## Notes

This section supports transport delivery guarantees and cross-transport
equivalence. It ensures runtime semantics are portable across ASGI servers rather
than coupled to one server's message extensions.
