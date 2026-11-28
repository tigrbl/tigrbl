from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import pytest

from tigrbl import TigrblApp, WebTransportBindingSpec
from tigrbl_concrete.system.docs.runtime_ops import register_runtime_websocket_route
from tigrbl_core._spec import TextFramingSpec
from tigrbl_kernel.protocol_chains.websocket import (
    build_websocket_jsonrpc_session_handler,
)
from tigrbl_kernel.session_lifecycle import SessionTermination
from tigrbl_ops_realtime import InMemoryRealtimeBroker


def _managed_websocket(app, broker):
    handler = build_websocket_jsonrpc_session_handler(app, realtime_broker=broker)
    register_runtime_websocket_route(
        app,
        path="/socket",
        alias="managed-session",
        endpoint=handler,
        handler_step=handler,
        framing="jsonrpc",
    )
    return _scope("websocket", "/socket")


def _scope(protocol, path, session_id="session-1"):
    scope = {
        "type": protocol,
        "path": path,
        "headers": [],
        "state": {},
        "query_string": b"",
        "extensions": {
            "tigr.transport_identity": {
                "version": 1,
                "connection_id": "carrier",
                "transport_session_id": session_id,
            },
        },
    }
    if protocol == "webtransport":
        scope.update(
            session_id=session_id,
            quic={"alpn": "h3"},
            ext={
                "transport": {"binding": "webtransport", "alpn": "h3", "secure": True},
                "webtransport": {"supports_bidi_streams": True},
            },
        )
        scope["extensions"]["tigr.transport_identity"]["http_stream_id"] = "0"
    return scope


def _webtransport(app, broker):
    app.__realtime_broker__ = broker

    async def echo():
        return "pong"

    app.add_route(
        "/wt",
        echo,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/wt",
            profile="bidi_stream",
            inner_framing=TextFramingSpec(),
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    return _scope("webtransport", "/wt")


@pytest.mark.asyncio
async def test_public_managed_websocket_dispatches_each_message_once(monkeypatch):
    app = TigrblApp()
    scope = _managed_websocket(app, None)
    calls = []
    sent = []

    async def rpc_call(model, alias, params, *, ctx):
        calls.append((model, alias, ctx["identity"]["invocation_id"]))
        return params

    async def unexpected(*args):
        pytest.fail("Realtime ASGI entered through the concrete invocation wrapper")

    monkeypatch.setattr(app, "rpc_call", rpc_call)
    monkeypatch.setattr(app, "invoke", unexpected)

    incoming = iter(
        [
            {"type": "websocket.connect"},
            *[
                {
                    "type": "websocket.receive",
                    "text": json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "method": "Device.echo",
                            "id": n,
                            "params": {"n": n},
                        }
                    ),
                }
                for n in (1, 2)
            ],
            {"type": "websocket.disconnect"},
        ]
    )

    async def receive():
        return next(incoming)

    async def send(event):
        sent.append(event)

    await app(scope, receive, send)

    assert [(model, alias) for model, alias, _ in calls] == [("Device", "echo")] * 2
    assert len({invocation for _, _, invocation in calls}) == 2
    assert [event["type"] for event in sent] == [
        "websocket.accept",
        "websocket.send",
        "websocket.send",
    ]
    assert [
        (reply["id"], reply["result"])
        for reply in (json.loads(event["text"]) for event in sent[1:])
    ] == [(1, {"n": 1}), (2, {"n": 2})]


@pytest.mark.asyncio
@pytest.mark.parametrize("protocol", ["websocket", "webtransport"])
@pytest.mark.parametrize(
    "signal", ["disconnect", "cancel", "receive_failure", "send_failure", "reply_failure"]
)
async def test_public_session_terminal_effects(protocol, signal, caplog):
    calls = []
    waiting = asyncio.Event()
    failure = OSError(f"{signal} on {protocol}")
    app = TigrblApp()

    async def disconnect_session(session_id):
        calls.append(("broker", session_id))
        raise RuntimeError("cleanup broker failure")

    async def disconnect_hub(session_id):
        calls.append(("hub", session_id))

    broker = SimpleNamespace(disconnect_session=disconnect_session)
    app.__presentation_hub__ = SimpleNamespace(disconnect=disconnect_hub)
    setup = _managed_websocket if protocol == "websocket" else _webtransport
    scope = setup(app, broker)
    events = [{"type": f"{protocol}.connect", "session_id": "session-1"}]
    if protocol == "webtransport":
        events.append({
            "type": "webtransport.stream.receive",
            "session_id": "session-1",
            "stream_id": "s1",
            "stream_direction": "bidi",
            "framing": "text",
            "data": b"ping",
            "more": True,
        })
    elif signal == "reply_failure":
        events.append({"type": "websocket.receive", "text": "not-json"})
    incoming = iter(events)

    async def receive():
        event = next(incoming, None)
        if event is not None:
            return event
        if signal == "receive_failure":
            raise failure
        if signal == "cancel":
            waiting.set()
            await asyncio.Future()
        assert signal == "disconnect"
        return {"type": f"{protocol}.disconnect", "session_id": "session-1"}

    async def send(event):
        kind = event["type"]
        if signal == "send_failure" and kind == f"{protocol}.accept":
            raise failure
        if signal == "reply_failure" and kind in {"websocket.send", "webtransport.stream.send"}:
            raise failure
        if kind == f"{protocol}.close":
            calls.append(("close", None))
            if signal in {"send_failure", "reply_failure"}:
                raise OSError("carrier unavailable during close")

    if signal == "cancel":
        task = asyncio.create_task(app(scope, receive, send))
        await asyncio.wait_for(waiting.wait(), 2)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    elif signal == "disconnect":
        await app(scope, receive, send)
    else:
        with pytest.raises(OSError) as caught:
            await app(scope, receive, send)
        assert caught.value is failure

    expected = [("broker", "session-1"), ("hub", "session-1")]
    if protocol == "websocket" and signal != "disconnect":
        expected.insert(1, ("close", None))
    if protocol == "webtransport" and signal == "disconnect":
        expected.insert(0, ("close", None))
    assert calls == expected
    assert "Realtime session cleanup effect failed" in caplog.text
    if protocol == "webtransport":
        state = scope["state"]["tigrbl_webtransport"]
        assert state["closed"]
        assert state["session"].streams["s1"].closed


@pytest.mark.asyncio
async def test_concurrent_terminal_signals_share_one_cleanup_even_when_waiter_is_cancelled():
    termination = SessionTermination()
    calls = []
    started = asyncio.Event()
    release = asyncio.Event()

    async def first_effect():
        calls.append("first")
        started.set()
        await release.wait()

    first = asyncio.create_task(
        termination.run(first_effect, lambda: calls.append("last"))
    )
    await started.wait()
    duplicate = asyncio.create_task(termination.run(lambda: calls.append("duplicate")))
    first.cancel("first signal")
    await asyncio.sleep(0)
    first.cancel("second signal")
    await asyncio.sleep(0)
    assert not first.done()
    release.set()
    # Python 3.10 can omit the cancellation message when awaiting the task.
    with pytest.raises(asyncio.CancelledError):
        await first
    await duplicate
    await termination.run(lambda: calls.append("late"))
    assert calls == ["first", "last"]


@pytest.mark.asyncio
@pytest.mark.parametrize("protocol", ["websocket", "webtransport"])
async def test_terminating_old_carrier_keeps_resumed_subscription(protocol):
    app = TigrblApp()
    broker = InMemoryRealtimeBroker()
    delivered = asyncio.Event()

    async def sink(event):
        delivered.set()

    destination = SimpleNamespace(send_realtime=sink)
    setup = _managed_websocket if protocol == "websocket" else _webtransport
    scope = setup(app, broker)
    try:
        original = await broker.subscribe(
            channel="updates", session_id="session-1", sink=destination
        )
        resumed = await broker.resume(
            original.subscription_id,
            expected_generation=original.generation,
            session_id="replacement",
            sink=destination,
            authorize=lambda *args: True,
        )
        assert resumed.generation != original.generation
        events = iter(
            [
                {"type": f"{protocol}.connect", "session_id": "session-1"},
                {"type": f"{protocol}.disconnect", "session_id": "session-1"},
            ]
        )

        async def receive():
            return next(events)

        async def send(event):
            pass

        await app(scope, receive, send)
        assert broker.subscriber_count("updates") == 1
        await broker.publish(channel="updates", event={"live": True})
        await asyncio.wait_for(delivered.wait(), 2)
        (delivery,) = broker.delivery_events()
        assert delivery["transport_session_id"] == "replacement"
        assert delivery["attachment_generation"] == resumed.generation
    finally:
        await broker.close()
