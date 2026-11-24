from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

import pytest

from tigrbl import WebTransportBindingSpec
from tigrbl_core._spec import TextFramingSpec
from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_core._spec.hook_types import HookPhase
from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_atoms.runtime_channel import WebTransportSessionState


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


from importlib.util import find_spec

if find_spec("tigrcorn_contract") is None:
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
            inner_framing=TextFramingSpec(),
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
        return {"type": "webtransport.disconnect", "session_id": scope.get("session_id", "session-1"), "code": 0}

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


def _wt_state(scope: dict[str, Any]) -> dict[str, Any]:
    return scope["state"]["tigrbl_webtransport"]


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
            inner_framing=TextFramingSpec(),
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
                "stream_initiator": "client",
                "framing": "text",
                "data": b"echo:alpha",
            "more": False,
        },
        {
            "type": "webtransport.stream.send",
                "session_id": "session-1",
                "stream_id": "bidi-2",
                "stream_direction": "bidi",
                "stream_initiator": "client",
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
        if item["phase"] == "ctx.channel_message"
    ] == [
        ("receive", "webtransport.connect", None, None),
        ("bidirectional", "webtransport.stream.receive", "bidi-1", None),
        ("bidirectional", "webtransport.stream.receive", "bidi-2", None),
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
        payload={"more": True, "session_id": "session-1", "stream_id": "bidi-1", "stream_direction": "bidi", "framing": "text"},
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


@pytest.mark.asyncio
async def test_webtransport_hook_trace_records_actual_execution() -> None:
    app = _app("/transport/multiplex")
    observed: list[dict[str, Any]] = []

    async def on_stream(ctx: dict[str, Any]) -> None:
        observed.append(dict(ctx["webtransport"]))

    app.hooks = (
        HookSpec(
            phase=HookPhase.PRE_HANDLER,
            fn=on_stream,
            family=("stream",),
            subevents=("stream.chunk.received",),
            name="wt-stream-ingress",
        ),
    )
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("hook-session"),
        webtransport_stream_receive(
            "hook-session",
            "bidi-1",
            b"alpha",
            stream_direction="bidi",
            framing="text",
        ),
        {"type": "webtransport.disconnect", "session_id": "hook-session", "code": 1000},
    ]

    await _run_contract_session(app, scope, events)

    hook_trace = _wt_state(scope)["hook_trace"]
    assert observed and observed[0]["session_id"] == "hook-session"
    assert observed[0]["stream_id"] == "bidi-1"
    assert hook_trace == [
        {
            "hook": "wt-stream-ingress",
            "phase": "PRE_HANDLER",
            "session_id": "hook-session",
            "stream_id": "bidi-1",
            "datagram_id": None,
            "stream_direction": "bidi",
            "lane": "bidi_stream",
            "family": "stream",
            "exchange": "bidirectional_stream",
            "event_type": "webtransport.stream.receive",
            "subevent": "stream.chunk.received",
            "framing": "text",
        }
    ]


@pytest.mark.asyncio
async def test_webtransport_hook_context_includes_session_and_stream_identity() -> None:
    app = _app("/transport/multiplex")
    contexts: list[dict[str, Any]] = []

    def capture(ctx: dict[str, Any]) -> None:
        contexts.append(dict(ctx["webtransport"]))

    app.hooks = (
        HookSpec(
            phase=HookPhase.PRE_HANDLER,
            fn=capture,
            family=("session", "stream", "datagram"),
            name="wt-context-capture",
        ),
    )
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("ctx-session"),
        webtransport_stream_receive(
            "ctx-session",
            "bidi-1",
            b"alpha",
            stream_direction="bidi",
            framing="text",
        ),
        webtransport_datagram_receive("ctx-session", "dg-client-1", b"ping", framing="text"),
        {"type": "webtransport.disconnect", "session_id": "ctx-session", "code": 1000},
    ]

    await _run_contract_session(app, scope, events)

    stream_ctx = next(item for item in contexts if item["event_type"] == "webtransport.stream.receive")
    datagram_ctx = next(item for item in contexts if item["event_type"] == "webtransport.datagram.receive")
    assert stream_ctx["session_id"] == "ctx-session"
    assert stream_ctx["stream_id"] == "bidi-1"
    assert stream_ctx["lane"] == "bidi_stream"
    assert datagram_ctx["session_id"] == "ctx-session"
    assert datagram_ctx["datagram_id"] == "dg-client-1"
    assert datagram_ctx["lane"] == "datagram"
    assert datagram_ctx["stream_id"] is None


@pytest.mark.asyncio
async def test_webtransport_datagram_events_reach_hooks_with_session_scope() -> None:
    app = _app("/transport/multiplex")
    datagrams: list[dict[str, Any]] = []

    def capture_datagram(ctx: dict[str, Any]) -> None:
        datagrams.append(dict(ctx["webtransport"]))

    app.hooks = (
        HookSpec(
            phase=HookPhase.PRE_HANDLER,
            fn=capture_datagram,
            family=("datagram",),
            subevents=("datagram.received",),
            name="wt-datagram-ingress",
        ),
    )
    scope = _scope("/transport/multiplex")
    events = [
        webtransport_connect("dg-session"),
        webtransport_datagram_receive("dg-session", "dg-client-1", b"ping", framing="json"),
        {"type": "webtransport.disconnect", "session_id": "dg-session", "code": 1000},
    ]

    await _run_contract_session(app, scope, events)

    assert datagrams == [
        {
            "session_id": "dg-session",
            "stream_id": None,
            "stream_direction": None,
            "datagram_id": "dg-client-1",
            "framing": "json",
            "lane": "datagram",
            "family": "datagram",
            "exchange": "bidirectional_stream",
            "event_type": "webtransport.datagram.receive",
            "subevent": "datagram.received",
            "event": {
                "type": "webtransport.datagram.receive",
                "session_id": "dg-session",
                "datagram_id": "dg-client-1",
                "data": b"ping",
                "framing": "json",
            },
        }
    ]


@pytest.mark.asyncio
async def test_webtransport_runtime_state_isolation_sequential_concurrent() -> None:
    app = _app("/transport/multiplex")

    async def run_session(session_id: str, stream_id: str) -> dict[str, Any]:
        scope = _scope("/transport/multiplex")
        events = [
            webtransport_connect(session_id),
            webtransport_stream_receive(
                session_id,
                stream_id,
                b"payload",
                stream_direction="bidi",
                framing="text",
            ),
        ]
        await _run_contract_session(app, scope, events)
        return scope

    first = await run_session("seq-a", "bidi-a")
    second = await run_session("seq-b", "bidi-b")
    concurrent_a, concurrent_b = await asyncio.gather(
        run_session("concurrent-a", "bidi-ca"),
        run_session("concurrent-b", "bidi-cb"),
    )

    assert _wt_state(first)["session"].session_id == "seq-a"
    assert _wt_state(second)["session"].session_id == "seq-b"
    assert _wt_state(first)["session"] is not _wt_state(second)["session"]
    assert {item.get("session_id") for item in _wt_state(concurrent_a)["trace"]} == {"concurrent-a"}
    assert {item.get("session_id") for item in _wt_state(concurrent_b)["trace"]} == {"concurrent-b"}
    assert _wt_state(concurrent_a)["session"] is not _wt_state(concurrent_b)["session"]


@pytest.mark.asyncio
async def test_webtransport_concurrent_scopes_each_multi_lane_burst_isolated() -> None:
    app = _app("/transport/multiplex")
    captured: list[dict[str, Any]] = []

    def capture(ctx: dict[str, Any]) -> None:
        captured.append(dict(ctx["webtransport"]))

    app.hooks = (
        HookSpec(
            phase=HookPhase.PRE_HANDLER,
            fn=capture,
            family=("stream", "datagram"),
            subevents=("stream.chunk.received", "datagram.received"),
            name="wt-burst-ingress",
        ),
        HookSpec(
            phase=HookPhase.POST_HANDLER,
            fn=capture,
            family=("stream", "datagram"),
            subevents=("stream.chunk.emit", "datagram.emit"),
            name="wt-burst-egress",
        ),
    )

    async def run_session(session_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        scope = _scope("/transport/multiplex")
        events = [
            webtransport_connect(session_id),
            webtransport_stream_receive(
                session_id,
                f"{session_id}-bidi-1",
                b"alpha",
                stream_direction="bidi",
                framing="text",
            ),
            webtransport_stream_receive(
                session_id,
                f"{session_id}-bidi-2",
                b"beta",
                stream_direction="bidi",
                framing="json",
            ),
            webtransport_stream_receive(
                session_id,
                f"{session_id}-upload-1",
                b'{"upload":1}\n',
                stream_direction="client_to_server",
                framing="ndjson",
            ),
            webtransport_datagram_receive(session_id, f"{session_id}-dg-1", b"ping", framing="text"),
            {"type": "webtransport.disconnect", "session_id": session_id, "code": 1000},
        ]
        sent = await _run_contract_session(app, scope, events)
        return scope, sent

    (scope_a, sent_a), (scope_b, sent_b) = await asyncio.gather(
        run_session("burst-a"),
        run_session("burst-b"),
    )

    for session_id, scope, sent in (("burst-a", scope_a, sent_a), ("burst-b", scope_b, sent_b)):
        trace = _wt_state(scope)["trace"]
        hook_trace = _wt_state(scope)["hook_trace"]
        assert {row.get("session_id") for row in trace if row.get("session_id")} == {session_id}
        assert {row.get("session_id") for row in hook_trace if row.get("session_id")} == {session_id}

        stream_dispatches = [
            row for row in trace if row.get("type") == "webtransport.stream.receive"
        ]
        assert sum(1 for row in stream_dispatches if row.get("stream_direction") == "bidi") == 2
        assert sum(1 for row in stream_dispatches if row.get("stream_direction") == "client_to_server") == 1
        assert any(row.get("type") == "webtransport.datagram.receive" for row in trace)

        ingress_lanes = {
            (row.get("event_type"), row.get("lane"))
            for row in hook_trace
            if row.get("phase") == "PRE_HANDLER"
        }
        egress_lanes = {
            (row.get("event_type"), row.get("lane"))
            for row in hook_trace
            if row.get("phase") == "POST_HANDLER"
        }
        assert ("webtransport.stream.receive", "bidi_stream") in ingress_lanes
        assert ("webtransport.stream.receive", "unidi_client_stream") in ingress_lanes
        assert ("webtransport.datagram.receive", "datagram") in ingress_lanes
        assert ("webtransport.stream.send", "bidi_stream") in egress_lanes
        assert ("webtransport.stream.send", "unidi_server_stream") in egress_lanes
        assert ("webtransport.datagram.send", "datagram") in egress_lanes

        for event in _stream_sends(sent) + _datagram_sends(sent):
            assert event["session_id"] == session_id

    assert {item["session_id"] for item in captured if item.get("session_id")} == {"burst-a", "burst-b"}


@pytest.mark.asyncio
async def test_webtransport_runtime_does_not_reuse_session_registry_between_scopes() -> None:
    app = _app("/transport/multiplex")
    scope_a = _scope("/transport/multiplex")
    scope_b = _scope("/transport/multiplex")

    await _run_contract_session(
        app,
        scope_a,
        [
            webtransport_connect("registry-a"),
            webtransport_stream_receive(
                "registry-a",
                "bidi-a",
                b"alpha",
                stream_direction="bidi",
                framing="text",
            ),
            {"type": "webtransport.disconnect", "session_id": "registry-a", "code": 1000},
        ],
    )
    await _run_contract_session(
        app,
        scope_b,
        [
            webtransport_connect("registry-b"),
            webtransport_stream_receive(
                "registry-b",
                "bidi-b",
                b"beta",
                stream_direction="bidi",
                framing="text",
            ),
            {"type": "webtransport.disconnect", "session_id": "registry-b", "code": 1000},
        ],
    )

    state_a = _wt_state(scope_a)
    state_b = _wt_state(scope_b)
    assert state_a["session"].session_id == "registry-a"
    assert state_b["session"].session_id == "registry-b"
    assert state_a["session"] is not state_b["session"]
    assert "bidi-a" in state_a["session"].streams
    assert "bidi-a" not in state_b["session"].streams
    assert state_a["trace"] is not state_b["trace"]


@pytest.mark.asyncio
async def test_webtransport_canonical_scope_correlation_isolates_two_sessions() -> None:
    app = _app("/transport/multiplex")

    async def run(session_id: str, carrier_stream: str):
        scope = _scope("/transport/multiplex")
        scope["session_id"] = session_id
        scope["extensions"] = {"tigr.transport_identity": {
            "version": 1, "connection_id": "quic-parent",
            "transport_session_id": session_id, "http_stream_id": carrier_stream,
        }}
        await _run_contract_session(app, scope, [
            webtransport_connect(session_id),
            webtransport_stream_receive(
                session_id, "bidi-1", b"alpha", stream_direction="bidi", framing="text"
            ),
            webtransport_datagram_receive(session_id, "datagram", b"data", framing="text"),
            {"type": "webtransport.disconnect", "session_id": session_id, "code": 1000},
        ])
        return _wt_state(scope)["trace"]

    left, right = await asyncio.gather(run("wt-1", "0"), run("wt-2", "4"))
    for session_id, trace in (("wt-1", left), ("wt-2", right)):
        inbound = [row for row in trace if row["phase"] == "ctx.channel_message"]
        assert {row["connection_id"] for row in inbound} == {"quic-parent"}
        assert {row["transport_session_id"] for row in inbound} == {session_id}
        assert len({row["correlation_id"] for row in inbound}) == 1
        streams = [row for row in inbound if row["type"] == "webtransport.stream.receive"]
        assert len(streams) == 1, inbound
        stream = streams[0]
        datagram, = [row for row in inbound if row["type"] == "webtransport.datagram.receive"]
        assert stream["stream_correlation_id"]
        assert "stream_correlation_id" not in datagram
        outbound_streams = [row for row in trace if row["type"] == "webtransport.stream.send"]
        assert outbound_streams and all(row["stream_correlation_id"] for row in outbound_streams)
        echo = next(row for row in outbound_streams if row["stream_id"] == stream["stream_id"])
        assert echo["stream_correlation_id"] == stream["stream_correlation_id"]
    assert left[0]["correlation_id"] != right[0]["correlation_id"]


@pytest.mark.asyncio
async def test_live_tigrcorn_webtransport_identity_drillback(tmp_path) -> None:
    fixture_root = os.environ.get("TIGRCORN_SOURCE_ROOT")
    if not fixture_root:
        pytest.skip("set TIGRCORN_SOURCE_ROOT to the Tigrcorn checkout to run the QUIC bridge")

    from importlib.util import module_from_spec, spec_from_file_location
    from tigr_asgi_contract import validate_transport_identity
    from tigrcorn.config.load import build_config
    from tigrcorn.server.runner import TigrCornServer
    from tigrcorn.transports.quic.handshake import generate_self_signed_certificate

    fixture = Path(fixture_root) / "tests/fixtures_third_party/wt_stream_client.py"
    spec = spec_from_file_location("tigrcorn_shared_wt_probe", fixture)
    assert spec is not None and spec.loader is not None
    client = module_from_spec(spec)
    sys.modules[spec.name] = client
    spec.loader.exec_module(client)

    app = TigrblApp(title="Live transport identity drillback")

    async def echo(ctx):
        return "ack"

    app.add_route(
        "/wt", echo, methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport", path="/wt", profile="bidi_stream",
            inner_framing=TextFramingSpec(),
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    completed = asyncio.Event()
    scopes = {}

    async def capture(scope, receive, send):
        advertised = scope["extensions"]["tigr.transport_identity"]
        identity = validate_transport_identity("webtransport", advertised, scope["session_id"])
        scopes[identity.transport_session_id] = scope

        async def verified_receive():
            event = await receive()
            validate_transport_identity("webtransport", advertised, scope["session_id"], event)
            if event["type"] == "webtransport.datagram.receive":
                if sum("received_datagram" in item for item in scopes.values()) == 1:
                    completed.set()
                scope["received_datagram"] = True
            return event

        await app(scope, verified_receive, send)

    cert, key = generate_self_signed_certificate("server.example")
    certfile, keyfile = tmp_path / "cert.pem", tmp_path / "key.pem"
    certfile.write_bytes(cert)
    keyfile.write_bytes(key)
    server = TigrCornServer(capture, build_config(
        transport="udp", host="127.0.0.1", port=0, lifespan="off",
        http_versions=["3"], protocols=["webtransport"],
        ssl_certfile=str(certfile), ssl_keyfile=str(keyfile),
        webtransport_path="/wt", webtransport_origins=["https://localhost:8088"],
        webtransport_max_sessions=2,
    ))
    await server.start()
    try:
        port = server._listeners[0].transport.get_extra_info("sockname")[1]
        result = await client.probe_wt_stream(
            "127.0.0.1", port, trusted_certificates=[cert], second_session=True,
            payload=b"first-stream", datagram_payload=b"first-datagram", close_connection=False,
            wait_for_datagram_response=False,
        )
        await asyncio.wait_for(completed.wait(), 3)
        assert result.status == 200
        assert len(scopes) == 2
        identities = [scope["state"]["_tigrbl_transport_identity"] for scope in scopes.values()]
        assert len({row["connection_id"] for row in identities}) == 1
        assert len({row["correlation_id"] for row in identities}) == 2
        for scope, identity in zip(scopes.values(), identities):
            rows = [row for row in _wt_state(scope)["trace"] if row["phase"] == "ctx.channel_message"]
            assert {row["correlation_id"] for row in rows} == {identity["correlation_id"]}
            assert any(row.get("stream_correlation_id") for row in rows)
            assert any(row.get("datagram_id") and "stream_correlation_id" not in row for row in rows)
    finally:
        await server.close()
