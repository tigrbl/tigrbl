from __future__ import annotations

import asyncio

import pytest

from tigrbl_runtime.channel import (
    RuntimeWebSocket,
    RuntimeWebSocketRoute,
    build_asgi_channel,
    complete_channel,
    normalize_exchange,
    prepare_channel_context,
)
from tigrbl_runtime.channel.asgi import send_transport_via_channel
from tigrbl_runtime.executors.types import _Ctx
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
            {
                "type": "websocket.receive",
                "text": '{"jsonrpc":"2.0","method":"widgets.echo","id":1}',
            },
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
    assert channel.state["connected"] is True
    assert ctx.get("body") is None
    assert "binding_protocol" not in ctx["temp"]["dispatch"]


def test_runtime_websocket_replays_buffered_receive_message() -> None:
    channel = OpChannel(
        kind="websocket",
        family="socket",
        exchange="bidirectional_stream",
        protocol="ws",
        path="/ws/echo",
        headers={"sec-websocket-protocol": "jsonrpc, demo"},
        state={"receive_queue": [{"type": "websocket.receive", "text": "hello"}]},
    )

    websocket = RuntimeWebSocket(channel)

    assert asyncio.run(websocket.receive_text()) == "hello"
    assert websocket.scope["subprotocols"] == ("jsonrpc", "demo")
    assert websocket.scope["headers"]["sec-websocket-protocol"] == "jsonrpc, demo"


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
    assert channel.state["selected_subprotocol"] == "jsonrpc"


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


def test_prepare_channel_context_traces_webtransport_receive_into_ctx() -> None:
    messages = iter(
        [
            {"type": "webtransport.connect", "session_id": "s1"},
            {
                "type": "webtransport.stream.receive",
                "session_id": "s1",
                "stream_id": "4",
                "stream_direction": "bidi",
                "framing": "text",
                "data": b"hello",
            },
        ]
    )

    async def _receive() -> dict[str, object]:
        return next(messages)

    scope = {
        "type": "webtransport",
        "scheme": "webtransport",
        "path": "/transport/session",
    }
    env = GwRawEnvelope(kind="asgi3", scope=scope, receive=_receive, send=_noop_send)
    ctx = {"temp": {}}

    channel = asyncio.run(prepare_channel_context(env, ctx))

    assert ctx["channel_message"]["type"] == "webtransport.stream.receive"
    assert ctx["body"] == b"hello"
    trace = scope["state"]["tigrbl_webtransport"]["trace"]
    assert trace == [
        {
            "direction": "receive",
            "phase": "ctx.channel_message",
            "type": "webtransport.connect",
            "binding": "webtransport",
            "event_type": "webtransport.connect",
            "subevent": "session.open",
            "family": "session",
            "lane": "session",
            "exchange": "request_response",
            "session_id": "s1",
        },
        {
            "direction": "bidirectional",
            "phase": "ctx.channel_message",
            "type": "webtransport.stream.receive",
            "binding": "webtransport",
            "event_type": "webtransport.stream.receive",
            "subevent": "stream.chunk.received",
            "family": "stream",
            "lane": "bidi_stream",
            "exchange": "bidirectional_stream",
            "session_id": "s1",
            "stream_id": "4",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "framing": "text",
            "payload_bytes": 5,
        },
    ]
    assert ctx["webtransport_trace"] is trace
    assert channel.state["webtransport_trace"] is trace


def test_eager_webtransport_drain_yields_under_continuous_media() -> None:
    calls = 0

    async def receive() -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 1:
            return {"type": "webtransport.connect", "session_id": "s1"}
        return {
            "type": "webtransport.stream.receive",
            "session_id": "s1",
            "stream_id": "2",
            "stream_direction": "client_to_server",
            "framing": "binary",
            "data": b"media",
            "more": True,
        }

    scope = {
        "type": "webtransport",
        "path": "/transport/session",
        "state": {"tigrbl_webtransport": {"eager_drain": True}},
    }
    env = GwRawEnvelope(kind="asgi3", scope=scope, receive=receive, send=_noop_send)
    ctx = {"temp": {}}

    channel = asyncio.run(prepare_channel_context(env, ctx))

    assert calls == 18
    assert len(channel.state["receive_queue"]) == 17


def test_send_transport_via_channel_emits_structured_webtransport_events() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = OpChannel(
        kind="webtransport",
        family="session",
        exchange="bidirectional_stream",
        protocol="webtransport",
        path="/transport/session",
        state={"session_id": "s1"},
    )
    ctx["channel_message"] = {
        "type": "webtransport.stream.receive",
        "session_id": "s1",
        "stream_id": "4",
        "stream_direction": "bidi",
        "framing": "binary",
    }
    ctx.temp = {
        "egress": {
            "transport_response": {
                "body": {
                    "bidirectional_streams": [{"message": "echo:payload"}],
                    "unidirectional_streams": [{"message": "demo-unidirectional"}],
                    "datagrams": [
                        {"direction": "client-to-server", "payload": "ping"},
                        {"direction": "server-to-client", "payload": "pong"},
                    ],
                }
            }
        }
    }

    asyncio.run(send_transport_via_channel(env, ctx))

    assert sent[0] == {"type": "webtransport.accept", "session_id": "s1"}
    assert sent[1] == {
        "type": "webtransport.stream.send",
        "session_id": "s1",
        "stream_id": "4",
        "stream_direction": "bidi",
        "stream_initiator": "client",
        "data": b"echo:payload",
        "more": False,
        "framing": "binary",
    }
    assert sent[2] == {
        "type": "webtransport.stream.send",
        "session_id": "s1",
        "stream_id": "server-stream-1",
        "stream_direction": "server_to_client",
        "stream_initiator": "server",
        "data": b"demo-unidirectional",
        "more": False,
    }
    assert sent[3] == {
        "type": "webtransport.datagram.send",
        "session_id": "s1",
        "datagram_id": "datagram-2",
        "data": b"pong",
    }
    assert len(sent) == 4
    assert not any(message["type"] == "webtransport.close" for message in sent)
    assert all(str(message["type"]).startswith("webtransport.") for message in sent)
    assert env.scope["state"]["tigrbl_webtransport"]["trace"] == [
        {
            "direction": "send",
            "phase": "transport.accept",
            "type": "webtransport.accept",
            "binding": "webtransport",
            "event_type": "webtransport.accept",
            "subevent": "session.accept",
            "family": "session",
            "lane": "session",
            "exchange": "request_response",
            "session_id": "s1",
        },
        {
            "direction": "bidirectional",
            "phase": "transport.emit",
            "type": "webtransport.stream.send",
            "binding": "webtransport",
            "event_type": "webtransport.stream.send",
            "subevent": "stream.chunk.emit",
            "family": "stream",
            "lane": "bidi_stream",
            "exchange": "bidirectional_stream",
            "session_id": "s1",
            "stream_id": "4",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "framing": "binary",
            "more": False,
            "payload_bytes": 12,
        },
        {
            "direction": "server_to_client",
            "phase": "transport.emit",
            "type": "webtransport.stream.send",
            "binding": "webtransport",
            "event_type": "webtransport.stream.send",
            "subevent": "stream.chunk.emit",
            "family": "stream",
            "lane": "unidi_server_stream",
            "exchange": "server_stream",
            "session_id": "s1",
            "stream_id": "server-stream-1",
            "stream_direction": "server_to_client",
            "stream_initiator": "server",
            "more": False,
            "payload_bytes": 19,
        },
        {
            "direction": "send",
            "phase": "transport.emit",
            "type": "webtransport.datagram.send",
            "binding": "webtransport",
            "event_type": "webtransport.datagram.send",
            "subevent": "datagram.emit",
            "family": "datagram",
            "lane": "datagram",
            "exchange": "bidirectional_stream",
            "session_id": "s1",
            "datagram_id": "datagram-2",
            "payload_bytes": 4,
        },
    ]


def test_send_transport_via_channel_rejects_invalid_webtransport_inbound_lane() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = OpChannel(
        kind="webtransport",
        family="session",
        exchange="bidirectional_stream",
        protocol="webtransport",
        path="/transport/session",
        state={"session_id": "s1"},
    )
    ctx["channel_message"] = {
        "type": "webtransport.stream.receive",
        "session_id": "s1",
        "stream_id": "4",
        "stream_direction": "server_to_client",
        "framing": "binary",
    }
    ctx.temp = {
        "egress": {
            "transport_response": {
                "body": {"bidirectional_streams": [{"message": "invalid"}]},
            }
        }
    }

    try:
        asyncio.run(send_transport_via_channel(env, ctx))
    except ValueError as exc:
        assert "server_to_client" in str(exc) or "receive events" in str(exc)
    else:
        raise AssertionError("invalid inbound WebTransport lanes must fail closed")
    assert sent == []


def test_send_transport_via_channel_closes_webtransport_disconnect_idempotently() -> (
    None
):
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = OpChannel(
        kind="webtransport",
        family="session",
        exchange="bidirectional_stream",
        protocol="webtransport",
        path="/transport/session",
        state={"session_id": "s1"},
    )
    ctx["channel_message"] = {
        "type": "webtransport.disconnect",
        "session_id": "s1",
        "code": 1001,
    }
    ctx.temp = {
        "egress": {"transport_response": {"body": {"datagrams": [{"payload": "pong"}]}}}
    }

    asyncio.run(send_transport_via_channel(env, ctx))

    assert sent == [{"type": "webtransport.close", "code": 1001, "session_id": "s1"}]


def _receive_only_channel(message: dict[str, object]) -> OpChannel:
    return OpChannel(
        kind="webtransport",
        family="session",
        exchange="bidirectional_stream",
        protocol="webtransport",
        path="/transport/session",
        state={
            "session_id": "s1",
            "receive_queue": [message],
            "event_projection": {
                "family": "stream",
                "lane": "unidi_client_stream",
                "exchange": "client_stream",
                "stream_direction": "client_to_server",
            },
        },
    )


def _receive_only_message() -> dict[str, object]:
    return {
        "type": "webtransport.stream.receive",
        "session_id": "s1",
        "stream_id": "6",
        "stream_direction": "client_to_server",
        "framing": "binary",
    }


def test_prepare_channel_context_records_receive_only_event_projection() -> None:
    messages = iter(
        [
            {"type": "webtransport.connect", "session_id": "s1"},
            {**_receive_only_message(), "data": b"upload"},
        ]
    )

    async def receive() -> dict[str, object]:
        return next(messages)

    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=receive,
        send=_noop_send,
    )
    ctx = {"temp": {}}

    channel = asyncio.run(prepare_channel_context(env, ctx))

    assert channel.state["event_projection"]["lane"] == "unidi_client_stream"
    assert channel.state["event_projection"]["exchange"] == "client_stream"
    assert ctx["channel_event_projection"] == channel.state["event_projection"]


def test_receive_only_webtransport_none_result_sends_nothing() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    message = _receive_only_message()
    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = _receive_only_channel(message)
    ctx["channel_message"] = message
    ctx.result = None
    ctx.temp = {"egress": {}}

    asyncio.run(send_transport_via_channel(env, ctx))

    assert sent == []
    assert "transport_sent" not in ctx["channel"].state
    assert ctx["channel"].state["egress_disposition"] == "suppressed_receive_only"
    assert ctx.temp["egress"] == {
        "response_suppressed": True,
        "suppression_reason": "receive_only_stream",
    }


def test_operation_projection_overrides_stale_shared_channel_projection() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    message = {
        "type": "webtransport.stream.receive",
        "session_id": "s1",
        "stream_id": "8",
        "stream_direction": "bidi",
        "framing": "binary",
    }
    env = GwRawEnvelope(
        kind="asgi3",
        scope={
            "type": "webtransport",
            "path": "/transport/session",
            "state": {"tigrbl_webtransport": {"accepted": True}},
        },
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = _receive_only_channel(_receive_only_message())
    ctx["channel_message"] = message
    ctx["channel_event_projection"] = {
        "family": "stream",
        "lane": "bidi_stream",
        "exchange": "bidirectional_stream",
        "stream_direction": "bidi",
    }
    ctx.temp = {
        "egress": {
            "transport_response": {
                "body": {"bidirectional_streams": [{"id": "8", "message": b"ok"}]}
            }
        }
    }

    asyncio.run(send_transport_via_channel(env, ctx))

    assert sent == [
        {
            "type": "webtransport.stream.send",
            "session_id": "s1",
            "stream_id": "8",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "data": b"ok",
            "more": False,
            "framing": "binary",
        }
    ]
    assert list(ctx["channel"].state["receive_queue"]) == []


def test_receive_only_webtransport_scalar_result_fails_before_send() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    message = _receive_only_message()
    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = _receive_only_channel(message)
    ctx["channel_message"] = message
    ctx.result = b"illegal echo"
    ctx.temp = {"egress": {}}

    with pytest.raises(ValueError, match="cannot automatically reply"):
        asyncio.run(send_transport_via_channel(env, ctx))

    assert sent == []


def test_receive_only_webtransport_allows_explicit_server_lanes() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    message = _receive_only_message()
    env = GwRawEnvelope(
        kind="asgi3",
        scope={
            "type": "webtransport",
            "path": "/transport/session",
            "state": {"tigrbl_webtransport": {"accepted": True}},
        },
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = _receive_only_channel(message)
    ctx["channel_message"] = message
    ctx.temp = {
        "egress": {
            "transport_response": {
                "body": {
                    "unidirectional_streams": [{"id": "ack-stream", "message": b"ack"}],
                    "datagrams": [{"id": "ack-dgram", "payload": b"seen"}],
                }
            }
        }
    }

    asyncio.run(send_transport_via_channel(env, ctx))

    assert [event["type"] for event in sent] == [
        "webtransport.stream.send",
        "webtransport.datagram.send",
    ]
    assert sent[0]["stream_direction"] == "server_to_client"
    assert ctx["channel"].state["transport_sent"] is True


def test_receive_only_webtransport_rejects_bidirectional_output() -> None:
    sent: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        sent.append(message)

    message = _receive_only_message()
    env = GwRawEnvelope(
        kind="asgi3",
        scope={"type": "webtransport", "path": "/transport/session"},
        receive=_empty_receive,
        send=send,
    )
    ctx = _Ctx()
    ctx["channel"] = _receive_only_channel(message)
    ctx["channel_message"] = message
    ctx.temp = {
        "egress": {
            "transport_response": {
                "body": {"bidirectional_streams": [{"message": "illegal"}]}
            }
        }
    }

    with pytest.raises(ValueError, match="bidirectional_streams output is invalid"):
        asyncio.run(send_transport_via_channel(env, ctx))

    assert sent == []
