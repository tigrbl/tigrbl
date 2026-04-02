# WebSockets and Server-Sent Events

## WebSockets

The framework now exposes a first-class websocket route surface:

- `router.websocket("/path")`
- `app.websocket("/path")`
- websocket dispatch and echo-style send/receive behavior are covered by the Phase 7 operator tests

## WHATWG SSE

The framework now exposes a first-class SSE surface:

- `EventStreamResponse(...)`
- event dictionaries are encoded to `text/event-stream`
- SSE body framing is covered by the Phase 7 operator tests

## Notes

This closure is at the framework/operator surface boundary. Transport/server protocol concerns remain delegated to the serving layer.
