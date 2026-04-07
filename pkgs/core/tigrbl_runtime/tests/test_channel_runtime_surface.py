from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_runtime.channel import build_asgi_channel, complete_channel, prepare_channel_context
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
