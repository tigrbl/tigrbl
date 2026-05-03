from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_runtime.channel import (
    RuntimeWebSocket,
    RuntimeWebSocketRoute,
    build_asgi_channel,
    complete_channel,
    normalize_exchange,
    prepare_channel_context,
)
from tigrbl_typing.channel import OpChannel
from tigrbl_typing.gw.raw import GwRawEnvelope


async def _empty_receive() -> dict[str, object]:
    return {"type": "http.request", "body": b"", "more_body": False}


async def _noop_send(_message: dict[str, object]) -> None:
    return None


def test_build_asgi_channel_classifies_http_stream_exchange() -> None:
    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "http", "scheme": "https", "path": "/events", "method": "GET"},
        receive=_empty_receive,
        send=_noop_send,
    )

    channel = build_asgi_channel(env, exchange="server_stream")

    assert isinstance(channel, OpChannel)
    assert channel.kind == "stream"
    assert channel.family == "stream"
    assert channel.protocol == "https"
    assert channel.selector == "GET /events"
    assert channel.subevents == ("receive", "emit", "complete")


def test_prepare_and_complete_channel_context_marks_post_emit() -> None:
    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "http", "scheme": "http", "path": "/widgets", "method": "POST"},
        receive=_empty_receive,
        send=_noop_send,
    )
    ctx = {"temp": {}}

    channel = asyncio.run(prepare_channel_context(env, ctx))
    asyncio.run(complete_channel(env, ctx))

    assert channel.path == "/widgets"
    assert ctx["transport_completed"] is True
    assert ctx["current_phase"] == "POST_EMIT"
    assert channel.state["completed"] is True
    assert channel.state["completion_fence"] == "POST_EMIT"


def test_prepare_channel_context_reads_initial_websocket_message() -> None:
    messages = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": '{"jsonrpc":"2.0","method":"widgets.echo","id":1}'},
        ]
    )

    async def _receive() -> dict[str, object]:
        return next(messages)

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "websocket", "scheme": "wss", "path": "/ws/widgets"},
        receive=_receive,
        send=_noop_send,
    )
    ctx = {"temp": {}}

    channel = asyncio.run(prepare_channel_context(env, ctx))

    assert channel.kind == "websocket"
    assert ctx["body"] == b'{"jsonrpc":"2.0","method":"widgets.echo","id":1}'
    assert ctx["temp"]["dispatch"]["binding_protocol"] == "wss.jsonrpc"
    assert channel.state["receive_queue"][0]["type"] == "websocket.receive"


def test_runtime_websocket_replays_buffered_receive_message() -> None:
    channel = OpChannel(
        kind="websocket",
        family="socket",
        exchange="bidirectional_stream",
        protocol="ws",
        path="/ws/echo",
        state={"receive_queue": [{"type": "websocket.receive", "text": "hello"}]},
    )

    websocket = RuntimeWebSocket(channel)

    assert asyncio.run(websocket.receive_text()) == "hello"


def test_concrete_websocket_export_is_runtime_websocket_facade() -> None:
    try:
        from tigrbl_concrete import WebSocket as ConcreteWebSocket
    except ImportError:
        import pytest

        pytest.xfail("tigrbl_concrete package root does not export WebSocket yet")

    assert ConcreteWebSocket is RuntimeWebSocket


def test_runtime_websocket_route_preserves_binding_metadata() -> None:
    async def handler(_websocket: RuntimeWebSocket) -> None:
        return None

    route = RuntimeWebSocketRoute(
        path_template="/ws/{item_id}",
        pattern=None,
        param_names=("item_id",),
        handler=handler,
        name="items.ws",
        protocol="wss",
        framing="jsonrpc",
        tags=["items"],
    )

    assert route.path_template == "/ws/{item_id}"
    assert route.param_names == ("item_id",)
    assert route.exchange == "bidirectional_stream"
    assert route.protocol == "wss"
    assert route.framing == "jsonrpc"
    assert route.tags == ["items"]


def test_runtime_websocket_accept_send_and_close_delegate_to_channel_send() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    channel = OpChannel(
        kind="websocket",
        family="socket",
        exchange="bidirectional_stream",
        protocol="wss",
        path="/ws/echo",
        send=send,
    )
    websocket = RuntimeWebSocket(channel)

    asyncio.run(websocket.accept(subprotocol="jsonrpc"))
    asyncio.run(websocket.send_text("hello"))
    asyncio.run(websocket.send_bytes(b"raw"))
    asyncio.run(websocket.close(code=1001))

    assert sent == [
        {"type": "websocket.accept", "subprotocol": "jsonrpc"},
        {"type": "websocket.send", "text": "hello"},
        {"type": "websocket.send", "bytes": b"raw"},
        {"type": "websocket.close", "code": 1001},
    ]
    assert websocket.accepted is True
    assert websocket.closed is True
    assert channel.state["closed"] is True


def test_runtime_websocket_receive_disconnect_marks_closed_state() -> None:
    channel = OpChannel(
        kind="websocket",
        family="socket",
        exchange="bidirectional_stream",
        protocol="ws",
        path="/ws/echo",
        state={"receive_queue": [{"type": "websocket.disconnect", "code": 1001}]},
    )
    websocket = RuntimeWebSocket(channel)

    message = asyncio.run(websocket.receive())

    assert message["type"] == "websocket.disconnect"
    assert websocket.closed is True
    assert channel.state["disconnected"] is True


def test_runtime_websocket_receive_text_raises_on_disconnect() -> None:
    channel = OpChannel(
        kind="websocket",
        family="socket",
        exchange="bidirectional_stream",
        protocol="ws",
        path="/ws/echo",
        state={"receive_queue": [{"type": "websocket.disconnect", "code": 1006}]},
    )
    websocket = RuntimeWebSocket(channel)

    try:
        asyncio.run(websocket.receive_text())
    except RuntimeError as exc:
        assert "disconnected" in str(exc)
    else:
        raise AssertionError("receive_text should fail on websocket disconnect")


def test_normalize_exchange_maps_legacy_bidirectional_value() -> None:
    assert normalize_exchange("bidirectional") == "bidirectional_stream"
