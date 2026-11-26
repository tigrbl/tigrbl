from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tigrbl_kernel.protocol_chains.websocket import (
    build_websocket_jsonrpc_session_handler,
)


@pytest.mark.asyncio
async def test_websocket_replies_use_each_authoritative_outcome_once() -> None:
    def rpc(case, **fields):
        return {"jsonrpc": "2.0", "method": "Record.delete", "params": {"case": case}, **fields}

    inbound = iter([
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps([
            rpc("ok", id=1), rpc("denied", id=2), rpc("denied-notification"),
        ])},
        {"type": "websocket.receive", "text": json.dumps(rpc("empty", id=3))},
        {"type": "websocket.disconnect", "code": 1000},
    ])
    calls = []
    sent = []

    async def receive():
        return next(inbound)

    async def send(message):
        sent.append(message)

    async def rpc_call(model, alias, params, **kwargs):
        case = params["case"]
        calls.append(case)
        denied = case.startswith("denied")
        body = {"detail": "Forbidden"} if denied else {"deleted": 1}
        return {
            "status_code": 403 if denied else 200,
            "body": b"" if case == "empty" else json.dumps(body).encode(),
            "body_iterator": None,
            "path": None,
        }

    router = SimpleNamespace(rpc_call=rpc_call)
    channel = SimpleNamespace(receive=receive, send=send, state={})
    await build_websocket_jsonrpc_session_handler(router)({"channel": channel, "temp": {}})
    batch, single = [json.loads(frame["text"]) for frame in sent if frame["type"] == "websocket.send"]
    assert calls == ["ok", "denied", "denied-notification", "empty"]
    assert [reply["id"] for reply in batch] == [1, 2]
    assert batch[0]["result"] == {"deleted": 1}
    assert batch[1]["error"]["code"] == -32002
    assert single == {"jsonrpc": "2.0", "id": 3, "result": None}


@pytest.mark.asyncio
async def test_jsonrpc_session_marks_transport_as_owned_after_accept() -> None:
    inbound = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1000},
    ]
    sent: list[dict] = []

    async def receive() -> dict:
        return inbound.pop(0)

    async def send(message: dict) -> None:
        sent.append(message)

    channel = SimpleNamespace(receive=receive, send=send, state={})
    handler = build_websocket_jsonrpc_session_handler(SimpleNamespace())

    await handler({"channel": channel, "temp": {}})

    assert sent == [{"type": "websocket.accept", "subprotocol": "jsonrpc"}]
    assert channel.state["transport_sent"] is True


@pytest.mark.asyncio
async def test_websocket_jsonrpc_dispatch_snapshots_binding_and_message_identity():
    import asyncio
    from tigrbl_core._spec import JsonRpcFramingSpec, WsBindingSpec
    from tigrbl_ops_realtime import InMemoryRealtimeBroker, subscribe

    requests = [
        {"jsonrpc": "2.0", "method": "Topic.subscribe", "params": {"channel": name}, "id": name}
        for name in ("one", "two", "three")
    ]
    messages = iter([
        {"type": "websocket.connect"},
        {"type": "websocket.receive", "text": json.dumps(requests[:2])},
        {"type": "websocket.receive", "text": json.dumps(requests[2])},
        {"type": "websocket.disconnect", "code": 1000},
    ])
    frames, seen = [], []

    class Topic:
        ops = SimpleNamespace(all=[SimpleNamespace(
            alias="subscribe", tx_scope="none",
            bindings=(WsBindingSpec(proto="ws", path="/controls", framing=JsonRpcFramingSpec(),
                                    subscription_ack_version=2),),
        )])

    async def receive():
        return next(messages)

    async def send(message):
        frames.append(message)

    async def rpc_call(model, alias, params, **kwargs):
        context = kwargs["ctx"]
        await asyncio.sleep(0)
        seen.append(context["identity"])
        result = await subscribe(params, ctx=context)
        return {"status_code": 200, "body": json.dumps(result).encode(),
                "body_iterator": None, "path": None}

    broker = InMemoryRealtimeBroker()
    from tigrbl_kernel.trace import Timeline

    timeline = Timeline()
    router = SimpleNamespace(tables={"Topic": Topic}, rpc_call=rpc_call, trace_sink=timeline.add)
    channel = SimpleNamespace(receive=receive, send=send, state={}, path="/controls")
    handler = build_websocket_jsonrpc_session_handler(router, realtime_broker=broker)
    await handler({"channel": channel, "temp": {"identity": {"transport_session_id": "ws-live"}}})
    batch, single = [json.loads(frame["text"]) for frame in frames if frame["type"] == "websocket.send"]
    assert [item["id"] for item in batch] == ["one", "two"]
    assert single["id"] == "three"
    for response in [*batch, single]:
        assert response["result"]["transport_session_id"] == "ws-live"
        assert response["result"]["subscription_id"] != "ws-live"
    assert seen[0]["invocation_id"] == seen[1]["invocation_id"] != seen[2]["invocation_id"]
    assert seen[0]["correlation_id"] == seen[1]["correlation_id"] != seen[2]["correlation_id"]
    assert [ctx.get("rpc_item_index") for ctx in seen] == [0, 1, None]
    assert len({ctx["span_id"] for ctx in seen}) == 3
    invocations = timeline.data()["events"]
    assert [item["kind"] for item in invocations] == ["Invocation"] * 3
    assert [item["span_id"] for item in invocations] == [item["span_id"] for item in seen]
    for item in invocations:
        assert (item["op_model"], item["op_alias"]) == ("Topic", "subscribe")
        assert item["timing_boundary"] == "invocation_monotonic"
        assert item["measured_duration_ms"] > 0
    assert broker.metrics()["subscriber_count"] == 0
