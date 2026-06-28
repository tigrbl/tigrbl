# Tigrbl WebSocket Realtime Ops Demo

This UV project observes the current `tigrbl_ops_realtime.subscribe` and
`tigrbl_ops_realtime.publish` behavior over a WebSocket server.

It is intentionally separate from the broader transport demo. The goal is to
watch one client subscribe to a channel while another client publishes to that
same channel.

## Run

```powershell
uv run --project .\examples\websocket_realtime_ops python -m tigrbl serve .\examples\websocket_realtime_ops\app.py:build_app --server uvicorn --host 127.0.0.1 --port 8000
```

## Test

```powershell
cd .\examples\websocket_realtime_ops
uv run pytest
```

Connect two WebSocket clients to:

```text
ws://127.0.0.1:8000/ws/realtime
```

Subscriber client:

```json
{"op":"subscribe","payload":{"channel":"thread:alpha","cursor":"msg-0"}}
```

Publisher client:

```json
{"op":"publish","payload":{"channel":"thread:alpha","event":{"message_id":"msg-1","body":"hello"}}}
```

Observed result: `subscribe` and `publish` return metadata envelopes. This
demo's in-memory registry forwards the publish result to subscribed WebSocket
clients so we can observe the broker-shaped behavior separately from the ops.
