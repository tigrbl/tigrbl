# WebSocket Realtime Lifecycle Working Decisions

This is a working decision log for the WebSocket realtime dispatch track. It is
not the SSOT record; promote the settled decisions into ADR/SPEC/feature rows
after the lifecycle and atom model is finalized.

## Accepted Working Decisions

1. WebSocket subprotocols are inferred from the framing spec.

   App code should declare the framing, not repeat the implied subprotocol.
   `JsonRpcFramingSpec()` implies JSON-RPC WebSocket subprotocol negotiation.
   App declarations should not need `subprotocols=("jsonrpc",)` when the
   framing spec already identifies JSON-RPC.

2. App WebSocket handlers must not implement operation dispatch loops.

   App code should not contain `if op == ...` switches, JSON parsing loops,
   `send_text` calls, broadcast loops, or `finally` blocks for framework-owned
   WebSocket mechanics. Those belong in compiled kernel plans and atoms.

3. Runtime executes the compiled kernel plan.

   Runtime should not own WebSocket lifecycle semantics, JSON-RPC dispatch,
   emission, broadcast, or cleanup policy. Runtime's job is to execute the
   packed kernel plan produced from AppSpec, binding specs, framing specs, op
   declarations, and atoms.

4. WebSocket open and close are structural lifecycle concerns.

   Opening/accepting a WebSocket connection and closing it are baked into the
   WebSocket binding lifecycle. They are not domain-specific app code and not
   subscription-specific behavior.

5. Domain-specific cleanup belongs to hooks.

   Subscription cleanup is not a hardcoded WebSocket close behavior. A
   `subscribe` op can use hooks to register domain cleanup/finalizers tied to
   the connection or subscription. The structural close lifecycle should provide
   the hook points needed to run cleanup before close, after close, or both.

6. Framing encode and decode are real atoms.

   The codec registry remains the pure implementation surface for frame
   serialization and parsing, but kernel plans should execute two first-class
   atoms: `framing.decode` and `framing.encode`. Those atoms call the selected
   codec for the binding/framing context, such as `jsonrpc` or
   `websocket.jsonrpc`, instead of embedding codec calls in app handlers or
   runtime-specific dispatch code.

7. WebSocket uses an outer session lifecycle around per-message operation
   lifecycles.

   The accepted phase ordering is:

   ```text
   SESSION_OPEN
   POST_SESSION_OPEN

   MESSAGE_RECEIVE
   INGRESS_PARSE
   INGRESS_DISPATCH
   PRE_TX_BEGIN
   START_TX
   PRE_HANDLER
   HANDLER
   POST_HANDLER
   PRE_COMMIT
   TX_COMMIT
   POST_COMMIT
   EGRESS_SHAPE
   EGRESS_FINALIZE
   POST_RESPONSE

   PRE_SESSION_CLOSE
   SESSION_CLOSE
   POST_SESSION_CLOSE
   ```

   `SESSION_OPEN` is the structural socket accept/open phase. `POST_SESSION_OPEN`
   is the hook point after accept and before the receive loop starts.
   `MESSAGE_RECEIVE` receives one WebSocket frame/message; each received message
   then runs through the existing operation lifecycle beginning with
   `INGRESS_PARSE` and `INGRESS_DISPATCH`. `PRE_SESSION_CLOSE` is the cleanup
   hook point before transport close, `SESSION_CLOSE` is the structural close
   phase, and `POST_SESSION_CLOSE` is the hook point after transport close.

8. Publish fanout is explicit and first-class.

   Publish fanout is handled by an explicit publish operation plus publish/fanout
   atoms. It is not automatic behavior of `create`, `send`, or other OLTP ops
   unless those ops explicitly declare a publish effect or hook. This preserves
   separate behaviors for create-only, create-and-publish, and publish-only
   workflows.

   Publish lifecycle placement is:

   ```text
   HANDLER         -> publish op validates/builds the publish intent
   POST_COMMIT     -> publish.prepare / publish.enqueue
   EGRESS_FINALIZE -> publish.fanout + framing.encode + transport.emit
   POST_RESPONSE   -> cleanup/metrics
   ```

   Subscription cleanup belongs in `PRE_SESSION_CLOSE` via a
   `subscription.unregister`-style hook/atom. The publish/fanout catalog should
   reuse the existing fanout pattern where possible, including shape/prepare
   before emission and delivery in the transport emission phase.

9. WebSocket bindings do not carry JSON-RPC method identity.

   `WsBindingSpec` and `WebSocketBindingSpec` declare transport reachability:
   protocol, connect path, exchange, framing, and inferred subprotocol. They do
   not need a WebSocket-specific `rpc_method` field. JSON-RPC method identity is
   derived from the executable `OpSpec` identity.

10. WebSocket-executable ops bind to the socket connect path.

    Every op executable over a WebSocket bidirectional session has a WebSocket
    binding whose `path` is the socket connect path. Multiple ops can share the
    same path, for example:

    ```text
    /ws/thread/{thread_id}
      Thread.subscribe
      Thread.publish
      Message.create
      Message.list
    ```

11. The kernel derives WebSocket JSON-RPC dispatch indexes from op identity and
    socket path.

    For JSON-RPC-framed WebSocket bindings, the kernel compiles both the
    structural session route and a derived JSON-RPC endpoint/method route:

    ```python
    proto_indices["ws"]["exact"][path] = session_program
    proto_indices["ws.jsonrpc"]["endpoints"][path][op_method] = op_program
    ```

    The `op_method` value comes from canonical op identity, not from the
    WebSocket binding. The compiler should reject duplicate `(path, op_method)`
    registrations.

12. Subscribe is a finite request/response operation that acks immediately.

    A `subscribe` op validates the request, registers session-scoped interest,
    returns a JSON-RPC acknowledgement, and completes. It does not own the
    WebSocket receive loop and does not remain running as a streaming handler.
    Future server-pushed subscription events are emitted by publish fanout, not
    by the subscribe handler.

13. Subscription registration and cleanup are atoms.

    Subscription registration and cleanup belong to atoms or hooks attached to
    the lifecycle, not app-local `finally` blocks. Registration should use
    `subscription.register`, preferably in `POST_COMMIT` for consistent
    post-commit visibility. Cleanup should use `subscription.unregister` in
    `PRE_SESSION_CLOSE`.

14. The core WebSocket realtime atom catalog is settled.

    The accepted core atom catalog includes:

    ```text
    transport.accept
    transport.receive
    transport.emit
    transport.close
    framing.decode
    framing.encode
    dispatch.binding.match
    dispatch.binding.parse
    subscription.register
    subscription.unregister
    publish.prepare
    publish.enqueue
    publish.fanout
    ```

    Publish fanout implementation details can still refine broker/session
    registry internals, but the atom categories and lifecycle placement are
    accepted.

## Decisions To Resolve Next

No open working decisions remain in this scratch log. The next step is to
promote the settled decisions into SSOT ADR/SPEC/feature records and then scope
implementation work.
