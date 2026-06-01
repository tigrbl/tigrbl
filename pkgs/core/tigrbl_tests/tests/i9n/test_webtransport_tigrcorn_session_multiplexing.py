from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

from tigrbl import WebTransportBindingSpec
from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_runtime.protocol.webtransport import WebTransportSessionState


def _install_adjacent_tigrcorn_sources() -> None:
    root = Path(__file__).resolve()
    for parent in root.parents:
        repo_parent = parent.parent
        tigrcorn = repo_parent / "tigrcorn"
        if not tigrcorn.exists():
            continue
        src_paths = [tigrcorn / "src", *(path / "src" for path in (tigrcorn / "pkgs").glob("*"))]
        for src_path in reversed(src_paths):
            if src_path.exists():
                value = str(src_path)
                if value not in sys.path:
                    sys.path.insert(0, value)
        return
    pytest.skip("adjacent tigrcorn checkout is required for this bridge test")


_install_adjacent_tigrcorn_sources()

from tigrcorn_contract import (  # noqa: E402
    project_receive_event,
    project_send_event,
    webtransport_connect,
    webtransport_datagram_receive,
    webtransport_stream_receive,
)


def _scope(path: str) -> dict[str, Any]:
    return {
        "type": "webtransport",
        "scheme": "webtransport",
        "path": path,
        "query_string": b"",
        "headers": [],
        "quic": {"alpn": "h3"},
        "ext": {
            "transport": {"binding": "webtransport", "alpn": "h3", "secure": True},
            "webtransport": {
                "supports_bidi_streams": True,
                "supports_uni_streams": True,
                "supports_datagrams": True,
            },
        },
    }


def _app(path: str) -> TigrblApp:
    app = TigrblApp(title="Tigrbl over Tigrcorn WebTransport Multiplexing")

    async def multiplex(ctx: Any) -> dict[str, Any]:
        return {
            "bidirectional_streams": [
                {"id": "bidi-1", "message": "reply-bidi-1"},
                {"id": "bidi-2", "message": "reply-bidi-2"},
            ],
            "unidirectional_streams": [
                {"id": "server-1", "message": "server-unidi-1", "framing": "text"},
            ],
            "datagrams": [
                {"id": "dg-server-1", "direction": "server-to-client", "payload": "pong-1", "framing": "json"},
                {"id": "dg-server-2", "direction": "server-to-client", "payload": "pong-2", "framing": "text"},
            ],
        }

    app.add_route(
        path,
        multiplex,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path=path,
            profile="bidi_stream",
            inner_framing="text",
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    return app


async def _run_contract_session(
    app: TigrblApp,
    scope: dict[str, Any],
    events: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []
    pending = list(events)
    scope.setdefault("state", {}).setdefault("tigrbl_webtransport", {})["eager_drain"] = True

    async def receive() -> dict[str, Any]:
        if pending:
            return pending.pop(0)
        return {"type": "webtransport.disconnect", "session_id": "session-1", "code": 0}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


async def _run_delayed_contract_session(
    app: TigrblApp,
    scope: dict[str, Any],
    events: list[dict[str, Any]],
    *,
    delayed_from_index: int,
) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []
    index = 0

    async def receive() -> dict[str, Any]:
        nonlocal index
        if index < len(events):
            if index >= delayed_from_index:
                await asyncio.sleep(0.01)
            event = events[index]
            index += 1
            return event
        return {"type": "webtransport.disconnect", "session_id": "session-1", "code": 0}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


def _stream_sends(sent: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in sent if event.get("type") == "webtransport.stream.send"]


def _datagram_sends(sent: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in sent if event.get("type") == "webtransport.datagram.send"]


@pytest.mark.asyncio
async def test_webtransport_tigrcorn_session_multiplexes_native_lanes() -> None:
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("session-1"),
        webtransport_stream_receive("session-1", "bidi-1", b"alpha", stream_direction="bidi", framing="text"),
        webtransport_stream_receive("session-1", "bidi-2", b"beta", stream_direction="bidi", framing="json"),
        webtransport_stream_receive(
            "session-1",
            "client-1",
            b'{"n":1}\n',
            stream_direction="client_to_server",
            framing="ndjson",
        ),
        webtransport_datagram_receive("session-1", "dg-client-1", b'{"ping":1}', framing="json"),
        webtransport_datagram_receive("session-1", "dg-client-2", b"ping-2", framing="text"),
    ]

    for event in events:
        assert project_receive_event(scope, event).scope_type == "webtransport"

    sent = await _run_contract_session(_app("/transport/multiplex"), scope, events)

    assert sent[0] == {"type": "webtransport.accept", "session_id": "session-1"}
    assert sent[-1] == {"type": "webtransport.close", "code": 1000, "session_id": "session-1"}
    assert sum(1 for event in sent if event.get("type") == "webtransport.accept") == 1
    assert sum(1 for event in sent if event.get("type") == "webtransport.close") == 1

    streams = _stream_sends(sent)
    datagrams = _datagram_sends(sent)
    assert {event["stream_id"] for event in streams if event["stream_direction"] == "bidi"} == {
        "bidi-1",
        "bidi-2",
    }
    assert any(event["stream_id"] == "server-1" and event["stream_direction"] == "server_to_client" for event in streams)
    assert {event["datagram_id"] for event in datagrams} == {"dg-server-1", "dg-server-2"}

    for event in streams + datagrams:
        projected = project_send_event(scope, event)
        assert projected.scope_type == "webtransport"
        assert event["session_id"] == "session-1"


@pytest.mark.asyncio
async def test_webtransport_tigrcorn_mixed_lane_framing_is_lane_local() -> None:
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("session-1"),
        webtransport_stream_receive("session-1", "bidi-1", b"alpha", stream_direction="bidi", framing="text"),
        webtransport_stream_receive("session-1", "bidi-2", b"beta", stream_direction="bidi", framing="json"),
        webtransport_datagram_receive("session-1", "dg-client-1", b'{"ping":1}', framing="json"),
        webtransport_datagram_receive("session-1", "dg-client-2", b"ping-2", framing="text"),
    ]

    sent = await _run_contract_session(_app("/transport/multiplex"), scope, events)
    by_stream = {event["stream_id"]: event for event in _stream_sends(sent)}
    by_datagram = {event["datagram_id"]: event for event in _datagram_sends(sent)}

    assert by_stream["bidi-1"]["framing"] == "text"
    assert by_stream["bidi-2"]["framing"] == "json"
    assert by_stream["server-1"]["framing"] == "text"
    assert by_datagram["dg-server-1"]["framing"] == "json"
    assert by_datagram["dg-server-2"]["framing"] == "text"


@pytest.mark.asyncio
async def test_webtransport_tigrcorn_session_stays_open_for_delayed_lanes() -> None:
    scope = _scope("/transport/echo-live")

    app = TigrblApp(title="Tigrbl WebTransport Live Multiplexing")

    async def echo(ctx: Any) -> str:
        body = ctx.get("body")
        if isinstance(body, (bytes, bytearray)):
            return f"echo:{bytes(body).decode('utf-8')}"
        return "echo:"

    app.add_route(
        "/transport/echo-live",
        echo,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/transport/echo-live",
            profile="bidi_stream",
            inner_framing="text",
        ),
        tigrbl_exchange="bidirectional_stream",
    )

    events = [
        webtransport_connect("session-1"),
        webtransport_stream_receive("session-1", "bidi-1", b"alpha", stream_direction="bidi", framing="text"),
        webtransport_stream_receive("session-1", "bidi-2", b"beta", stream_direction="bidi", framing="text"),
        webtransport_datagram_receive("session-1", "dg-client-1", b"ping", framing="text"),
        {"type": "webtransport.disconnect", "session_id": "session-1", "code": 1000},
    ]

    sent = await _run_delayed_contract_session(
        app,
        scope,
        events,
        delayed_from_index=2,
    )

    stream_sends = _stream_sends(sent)
    datagram_sends = _datagram_sends(sent)

    assert sum(1 for event in sent if event.get("type") == "webtransport.accept") == 1
    assert stream_sends == [
        {
            "type": "webtransport.stream.send",
            "session_id": "session-1",
            "stream_id": "bidi-1",
            "stream_direction": "bidi",
            "framing": "text",
            "data": b"echo:alpha",
            "more": False,
        },
        {
            "type": "webtransport.stream.send",
            "session_id": "session-1",
            "stream_id": "bidi-2",
            "stream_direction": "bidi",
            "framing": "text",
            "data": b"echo:beta",
            "more": False,
        },
    ]
    assert datagram_sends == [
        {
            "type": "webtransport.datagram.send",
            "session_id": "session-1",
            "datagram_id": "dg-client-1",
            "framing": "text",
            "data": b"echo:ping",
        },
    ]
    assert sent[-1] == {"type": "webtransport.close", "code": 1000, "session_id": "session-1"}
    trace = scope["state"]["tigrbl_webtransport"]["trace"]
    assert [
        (item["direction"], item["type"], item.get("stream_id"), item.get("datagram_id"))
        for item in trace
        if item["direction"] == "receive"
    ] == [
        ("receive", "webtransport.connect", None, None),
        ("receive", "webtransport.stream.receive", "bidi-1", None),
        ("receive", "webtransport.stream.receive", "bidi-2", None),
        ("receive", "webtransport.datagram.receive", None, "dg-client-1"),
        ("receive", "webtransport.disconnect", None, None),
    ]
    latest_trace = getattr(app, "_webtransport_trace_latest")
    trace_snapshots = getattr(app, "_webtransport_trace_snapshots")
    assert latest_trace is not trace
    assert latest_trace == trace
    assert trace_snapshots[-1] == trace


@pytest.mark.asyncio
async def test_webtransport_tigrcorn_rejects_native_message_lane() -> None:
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("session-1"),
        {"type": "webtransport.message.receive", "session_id": "session-1", "data": b"not-native"},
    ]

    with pytest.raises(ValueError, match="message is not a native transport lane"):
        await _run_contract_session(_app("/transport/multiplex"), scope, events)


def test_webtransport_tigrcorn_session_close_cascade_blocks_late_lanes() -> None:
    session = WebTransportSessionState(session_id="session-1")
    session.apply_event(event="webtransport.accept", channel="send", payload={"session_id": "session-1"})
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "session-1", "stream_id": "bidi-1", "stream_direction": "bidi", "framing": "text"},
    )
    session.apply_event(
        event="webtransport.datagram.receive",
        channel="receive",
        payload={"session_id": "session-1", "datagram_id": "dg-client-1", "framing": "json"},
    )

    closed = session.apply_event(event="webtransport.close", channel="send", payload={"session_id": "session-1"})

    assert closed["closed"] is True
    assert closed["streams"]["bidi-1"]["closed"] is True
    with pytest.raises(ValueError, match="session is closed"):
        session.apply_event(
            event="webtransport.datagram.send",
            channel="send",
            payload={"session_id": "session-1", "datagram_id": "dg-server-late", "framing": "json"},
        )
