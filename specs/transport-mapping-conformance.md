# Transport Mapping Conformance

Date: 2026-04-07
Phase: 2

## Intent

This document records the repository-owned transport mapping model used by the
Phase 2 runtime/kernel transport checkpoint.

## Mapping

| Declared binding | Runtime channel kind | Runtime family | Default subevents | Notes |
| --- | --- | --- | --- | --- |
| `HttpRestBindingSpec` | `http` | `response` | `receive, emit, complete` | request/response HTTP |
| `HttpStreamBindingSpec` | `stream` | `stream` | `receive, emit, complete` | long-lived HTTP body stream |
| `SseBindingSpec` | `sse` | `stream` | `receive, emit, complete` | server event stream over HTTP |
| `WsBindingSpec` | `websocket` | `socket` | `connect, receive, emit, complete, disconnect` | path-routed runtime websocket execution |
| `WsBindingSpec(..., framing="jsonrpc")` | `websocket` | `socket` | `connect, receive, emit, complete, disconnect` | JSON-RPC framing over WS/WSS |
| `WebTransportBindingSpec` | `webtransport` | `session` | `connect, receive, emit, complete, disconnect` | explicit session transport |

## Current checkpoint behavior

- Python runtime owns ASGI channel preparation and completion tracking.
- Python concrete now hands runtime DB/session resolution callbacks instead of
  being imported by runtime executors.
- Declared websocket and WebTransport bindings resolve by compiled plan path.
- Legacy websocket decorators still work, but they are dispatched from runtime
  as a compatibility fallback rather than from a direct app bypass.
- `POST_EMIT` is represented as a deterministic runtime completion marker on the
  context after transport completion. This checkpoint does not yet add a full
  compiled hook phase for `POST_EMIT`.

## Outstanding work

- Native Rust runtime execution still mirrors the channel contract but does not
  yet execute live transport loops for all exchanges.
- HTTP stream, SSE, and WebTransport runtime loops remain partially represented
  through the ASGI channel adapter and response emission path rather than a
  dedicated per-family executor.
- Full release certification for `0.3.19.dev1` remains blocked.
