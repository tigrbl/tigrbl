from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pytest

from tigrbl import WebTransportBindingSpec
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.hook_types import HookPhase
from tigrbl_concrete._concrete._app import App as TigrblApp


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
    pytest.skip("adjacent tigrcorn checkout is required for this bridge test", allow_module_level=True)


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
    app = TigrblApp(title="Tigrbl over Tigrcorn WebTransport Bridge")

    async def echo(ctx: Any) -> str:
        getter = getattr(ctx, "get", None)
        body = getter("body") if callable(getter) else None
        if isinstance(body, (bytes, bytearray)):
            return f"echo:{bytes(body).decode('utf-8')}"
        return "echo:"

    app.add_route(
        path,
        echo,
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

    async def receive() -> dict[str, Any]:
        if pending:
            return pending.pop(0)
        return {"type": "webtransport.disconnect", "session_id": "session-1", "code": 0}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


@pytest.mark.asyncio
async def test_tigrbl_webtransport_bidi_stream_runs_over_tigrcorn_contract_events() -> None:
    scope = _scope("/transport/echo")
    connect = webtransport_connect("session-1")
    stream = webtransport_stream_receive(
        "session-1",
        "stream-1",
        b"hello",
        stream_direction="bidi",
        framing="text",
    )

    assert project_receive_event(scope, connect).family == "session"
    incoming = project_receive_event(scope, stream)
    assert (incoming.family, incoming.exchange, incoming.direction) == (
        "stream",
        "duplex",
        "client_to_server",
    )

    sent = await _run_contract_session(_app("/transport/echo"), scope, [connect, stream])

    assert sent[0] == {"type": "webtransport.accept", "session_id": "session-1"}
    assert sent[1] == {
        "type": "webtransport.stream.send",
        "session_id": "session-1",
        "stream_id": "stream-1",
        "stream_direction": "bidi",
        "framing": "text",
        "data": b"echo:hello",
        "more": False,
    }
    outgoing = project_send_event(scope, sent[1])
    assert (outgoing.family, outgoing.exchange, outgoing.direction) == (
        "stream",
        "duplex",
        "server_to_client",
    )


@pytest.mark.asyncio
async def test_tigrbl_webtransport_datagram_runs_over_tigrcorn_contract_events() -> None:
    scope = _scope("/transport/echo")
    connect = webtransport_connect("session-1")
    datagram = webtransport_datagram_receive(
        "session-1",
        "datagram-1",
        b"ping",
        framing="text",
    )

    incoming = project_receive_event(scope, datagram)
    assert (incoming.family, incoming.exchange, incoming.direction) == (
        "datagram",
        "duplex",
        "client_to_server",
    )

    sent = await _run_contract_session(_app("/transport/echo"), scope, [connect, datagram])

    assert sent[0] == {"type": "webtransport.accept", "session_id": "session-1"}
    assert sent[1] == {
        "type": "webtransport.datagram.send",
        "session_id": "session-1",
        "datagram_id": "datagram-1",
        "framing": "text",
        "data": b"echo:ping",
    }
    outgoing = project_send_event(scope, sent[1])
    assert (outgoing.family, outgoing.exchange, outgoing.direction) == (
        "datagram",
        "duplex",
        "server_to_client",
    )


@pytest.mark.asyncio
async def test_webtransport_bidi_and_unidi_lane_metadata_reaches_hooks() -> None:
    app = TigrblApp(title="Tigrbl WebTransport Lane Metadata")
    captured: list[dict[str, Any]] = []

    def capture(ctx: dict[str, Any]) -> None:
        captured.append(dict(ctx["webtransport"]))

    async def lanes(ctx: Any) -> dict[str, Any]:
        return {
            "bidirectional_streams": [{"id": "bidi-1", "message": "reply-bidi"}],
            "unidirectional_streams": [
                {"id": "server-1", "message": "server-unidi", "framing": "text"}
            ],
        }

    app.hooks = (
        HookSpec(
            phase=HookPhase.PRE_HANDLER,
            fn=capture,
            family=("stream",),
            subevents=("stream.chunk.received",),
            name="wt-stream-lane-ingress",
        ),
        HookSpec(
            phase=HookPhase.POST_HANDLER,
            fn=capture,
            family=("stream",),
            subevents=("stream.chunk.emit",),
            name="wt-stream-lane-egress",
        ),
    )
    app.add_route(
        "/transport/lanes",
        lanes,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/transport/lanes",
            profile="bidi_stream",
            inner_framing="text",
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    scope = _scope("/transport/lanes")
    scope.setdefault("state", {}).setdefault("tigrbl_webtransport", {})["eager_drain"] = True
    events = [
        webtransport_connect("lane-session"),
        webtransport_stream_receive(
            "lane-session",
            "bidi-1",
            b"alpha",
            stream_direction="bidi",
            framing="text",
        ),
        webtransport_stream_receive(
            "lane-session",
            "client-1",
            b"upload",
            stream_direction="client_to_server",
            framing="text",
        ),
        {"type": "webtransport.disconnect", "session_id": "lane-session", "code": 1000},
    ]

    sent = await _run_contract_session(app, scope, events)

    lanes_by_stream = {item["stream_id"]: item["lane"] for item in captured if item["stream_id"]}
    assert lanes_by_stream["bidi-1"] == "bidi_stream"
    assert lanes_by_stream["client-1"] == "unidi_client_stream"
    assert any(
        item["stream_id"] == "server-1" and item["lane"] == "unidi_server_stream"
        for item in captured
    )
    assert any(
        event.get("stream_id") == "server-1"
        and event.get("stream_direction") == "server_to_client"
        for event in sent
    )
