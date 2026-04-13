# WebSockets and Server-Sent Events

## WebSockets

The framework now exposes a first-class websocket route surface:

- `router.websocket("/path")`
- `app.websocket("/path")`
- websocket route declarations are compiled into runtime-owned channel ops
- websocket dispatch and echo-style send/receive behavior are covered by the Phase 7 operator tests

## WHATWG SSE

The framework now exposes a first-class SSE surface:

- `EventStreamResponse(...)`
- event dictionaries are encoded to `text/event-stream`
- SSE body framing is covered by the Phase 7 operator tests

## Notes

This closure is at the framework/operator surface boundary. Runtime now owns
the websocket execution path, while transport/server protocol concerns still
remain delegated to the serving layer.
