# Tigrbl WebSocket Realtime JSON-RPC Framework Demo

This UV project demonstrates the canonical framework declaration shape for
WebSocket realtime JSON-RPC ops:

- `AppSpec`
- `RouterSpec`
- `PathSpec(kind="ws-jsonrpc")`
- `TableSpec`
- `OpSpec`

The ops share one WebSocket connect path, use `JsonRpcFramingSpec`, infer the
`jsonrpc` subprotocol from framing, and lower through `TigrblApp.from_spec(...)`
into a route whose WebSocket JSON-RPC session behavior is composed by the
kernel from transport, framing, dispatch, and emit atoms.

It does not implement an app-local receive loop, JSON parser, op switch, send
loop, broadcast loop, or cleanup block. Those are kernel/atom/runtime
responsibilities governed by `adr:1199` and `spc:1147`.

## Test

```powershell
cd .\examples\websocket_realtime_ops
uv run pytest
```

## Declared Ops

```text
/ws/realtime
  Thread
    subscribe -> target=subscribe
    publish   -> target=publish
  Message
    create    -> target=create
```

`Thread.subscribe` is modeled as a finite JSON-RPC request/response op that
acknowledges registration. `Thread.publish` is modeled as an explicit fanout op.
`Message.create` is present to show that OLTP create does not publish unless a
publish effect is declared.
