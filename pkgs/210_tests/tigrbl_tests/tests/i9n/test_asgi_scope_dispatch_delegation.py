from __future__ import annotations

import json

import pytest

from tigrbl import TigrblApp, WebTransportBindingSpec
from tigrbl_atoms import protocol_scope
from tigrbl_core._spec import TextFramingSpec
from tigrbl_kernel import asgi_dispatch
from tigrbl_kernel.trace import Timeline
from tigrbl_kernel.webtransport_session_plan import WebTransportSessionPlan


class GuardedScope(dict):
    type_reads = 0

    def _read(self, key):
        if key == "type":
            self.type_reads += 1
            assert self.type_reads == 1, "raw ASGI scope type read more than once"

    def get(self, key, default=None):
        self._read(key)
        return super().get(key, default)

    def __getitem__(self, key):
        self._read(key)
        return super().__getitem__(key)


def _instrument_handoff(monkeypatch, app):
    calls = []
    runtime = app.runtime
    real_dispatch = runtime.dispatch_asgi
    real_entry = runtime._asgi_entry_point
    raw_calls = []
    real_project = protocol_scope.project_asgi_scope
    real_select = asgi_dispatch.select_asgi_ingress

    async def dispatch(scope, receive, send):
        raw_calls.append((scope, receive, send))
        calls.append(("runtime", scope))
        await real_dispatch(scope, receive, send)

    async def entry(scope, receive, send):
        assert all(original is actual for original, actual in zip(
            raw_calls.pop(), (scope, receive, send)
        ))
        calls.append(("kernel-entry", scope))
        await real_entry(scope, receive, send)

    def project(scope):
        projected = real_project(scope)
        calls.append(("projector", projected))
        return projected

    def select(projected):
        assert projected is calls[-1][1]
        calls.append(("kernel", projected))
        return real_select(projected)

    monkeypatch.setattr(runtime, "dispatch_asgi", dispatch)
    monkeypatch.setattr(runtime, "_asgi_entry_point", entry)
    monkeypatch.setattr(protocol_scope, "project_asgi_scope", project)
    monkeypatch.setattr(asgi_dispatch, "select_asgi_ingress", select)
    return calls


async def _call(app, scope, incoming):
    sent = []
    messages = iter(incoming)

    async def receive():
        return next(messages)

    async def send(message):
        sent.append(message)

    await app(scope, receive, send)
    return sent


def _assert_handoff(calls, scope, kind):
    assert scope.type_reads == 1
    assert [owner for owner, _ in calls] == ["runtime", "kernel-entry", "projector", "kernel"]
    assert calls[0][1] is scope
    assert calls[1][1] is scope
    assert calls[2][1] is calls[3][1]
    assert calls[3][1].kind is kind


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/ping", "/missing"], ids=["matched", "fallback"])
async def test_http_dispatch_reuses_projection_for_tracing_and_completion(
    monkeypatch, path
):
    timeline = Timeline()
    app = TigrblApp(trace_sink=timeline.add)
    calls = _instrument_handoff(monkeypatch, app)

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    scope = GuardedScope(
        type="http", method="GET", path=path, headers=[], query_string=b""
    )
    sent = await _call(app, scope, [{"type": "http.request", "body": b""}])
    _assert_handoff(calls, scope, protocol_scope.AsgiScopeKind.HTTP)
    assert sent[0]["status"] == (200 if path == "/ping" else 404)
    assert b"x-correlation-id" in dict(sent[0]["headers"])
    assert sent[-1]["type"] == "http.response.body"
    assert not sent[-1].get("more_body")
    assert {row["kind"] for row in timeline.data()["events"]} >= {
        "Scope opened",
        "Response",
    }
    if path == "/ping":
        assert json.loads(sent[-1]["body"]) == {"ok": True}


@pytest.mark.asyncio
async def test_websocket_dispatch_reuses_projection_for_session(monkeypatch):
    app = TigrblApp()
    calls = _instrument_handoff(monkeypatch, app)
    seen = []

    @app.websocket("/socket")
    async def socket(websocket):
        await websocket.accept()
        seen.append(await websocket.receive_text())
        await websocket.send_text("echo:" + seen[-1])
        await websocket.close(code=1000)

    scope = GuardedScope(type="websocket", path="/socket", headers=[], query_string=b"")
    sent = await _call(
        app,
        scope,
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": "hello"},
            {"type": "websocket.disconnect", "code": 1000},
        ],
    )
    _assert_handoff(calls, scope, protocol_scope.AsgiScopeKind.WEBSOCKET)
    assert seen == ["hello"]
    assert any(message["type"] == "websocket.accept" for message in sent)
    assert any(message.get("text") == "echo:hello" for message in sent)
    assert sent[-1] == {"type": "websocket.close", "code": 1000}


@pytest.mark.asyncio
async def test_webtransport_dispatch_reuses_projection_for_session(monkeypatch):
    app = TigrblApp()
    path = "/transport"
    calls = _instrument_handoff(monkeypatch, app)
    invocations = []
    entries = []
    original_run = WebTransportSessionPlan.run

    async def run(plan, scope, invoke, snapshot):
        entries.append(plan)
        await original_run(plan, scope, invoke, snapshot)

    monkeypatch.setattr(WebTransportSessionPlan, "run", run)

    async def echo(ctx):
        message = ctx["channel_message"]
        invocations.append(message["type"])
        if message["type"] == "webtransport.datagram.receive":
            session = ctx["channel"].state["webtransport_session"]
            assert session.streams["stream-1"].closed
            assert not session.closed
        return "echo"

    app.add_route(
        path,
        echo,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path=path,
            profile="bidi_stream",
            inner_framing=TextFramingSpec(),
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    scope = GuardedScope(
        type="webtransport",
        path=path,
        headers=[],
        state={},
        query_string=b"",
        quic={"alpn": "h3"},
        ext={
            "transport": {"binding": "webtransport", "alpn": "h3", "secure": True},
            "webtransport": {
                "supports_bidi_streams": True,
                "supports_uni_streams": True,
                "supports_datagrams": True,
            },
        },
    )
    datagram = {
        "type": "webtransport.datagram.receive",
        "session_id": "session-1",
        "datagram_id": "d-1",
        "data": b"ping",
        "framing": "text",
    }
    def stream(data):
        return {
            "type": "webtransport.stream.receive",
            "session_id": "session-1",
            "stream_id": "stream-1",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "framing": "text",
            "data": data,
            "more": True,
        }

    sent = await _call(
        app,
        scope,
        [
            {"type": "webtransport.connect", "session_id": "session-1"},
            stream(b"hello"),
            {
                "type": "webtransport.stream.close",
                "session_id": "session-1",
                "stream_id": "stream-1",
            },
            stream(b"late stream data"),
            datagram,
            {"type": "webtransport.disconnect", "session_id": "session-1", "code": 0},
            dict(datagram, datagram_id="late"),
        ],
    )
    _assert_handoff(calls, scope, protocol_scope.AsgiScopeKind.WEBTRANSPORT)
    state = scope["state"]["tigrbl_webtransport"]
    assert entries == [state["session_plan"]]
    assert invocations == ["webtransport.stream.receive", "webtransport.datagram.receive"]
    assert sent[0] == {"type": "webtransport.accept", "session_id": "session-1"}
    assert sent[1]["type"] == "webtransport.stream.send"
    assert sent[1]["data"] == b"echo"
    assert sent[2]["type"] == "webtransport.datagram.send"
    assert sent[2]["datagram_id"] == "d-1"
    assert sent[3]["type"] == "webtransport.close"
    assert state["session"].closed


@pytest.mark.asyncio
async def test_lifespan_dispatch_runs_app_handlers_through_selected_plan(monkeypatch):
    app = TigrblApp()
    calls = _instrument_handoff(monkeypatch, app)
    notifications = []

    @app.on_event("startup")
    async def startup():
        notifications.append("startup")

    @app.on_event("shutdown")
    async def shutdown():
        notifications.append("shutdown")

    scope = GuardedScope(type="lifespan")
    sent = await _call(
        app, scope, [{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}]
    )
    _assert_handoff(calls, scope, protocol_scope.AsgiScopeKind.LIFESPAN)
    assert notifications == ["startup", "shutdown"]
    assert sent == [
        {"type": "lifespan.startup.complete"},
        {"type": "lifespan.shutdown.complete"},
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("values", [{}, {"type": None}, {"type": "unknown"}])
async def test_invalid_scope_fails_before_kernel_selection(monkeypatch, values):
    app = TigrblApp()
    calls = _instrument_handoff(monkeypatch, app)
    scope = GuardedScope(values)
    with pytest.raises(ValueError, match="scope type"):
        await _call(app, scope, [])
    assert scope.type_reads == 1
    assert [owner for owner, _ in calls] == ["runtime", "kernel-entry"]


@pytest.mark.asyncio
async def test_jsonrpc_batch_reuses_ingress_projection_and_selection(
    monkeypatch, app_client
):
    _, app, _ = app_client
    calls = _instrument_handoff(monkeypatch, app)
    reads = []
    read_type = protocol_scope._read_scope_type

    def count_reads(scope):
        reads.append(scope)
        return read_type(scope)

    monkeypatch.setattr(protocol_scope, "_read_scope_type", count_reads)
    scope = GuardedScope(
        type="http",
        method="POST",
        path="/rpc/",
        query_string=b"",
        headers=[(b"content-type", b"application/json")],
    )
    batch = [
        {"jsonrpc": "2.0", "id": 1, "method": "Tenant.list", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "Tenant.list", "params": {}},
    ]
    sent = await _call(
        app, scope, [{"type": "http.request", "body": json.dumps(batch).encode()}]
    )
    assert sent[0]["status"] == 200
    result = json.loads(sent[-1]["body"])
    assert [item["id"] for item in result] == [1, 2]
    assert all("result" in item for item in result), result
    assert scope.type_reads == 1
    assert len(reads) == 1 and reads[0] is scope
    selected = [value for owner, value in calls if owner == "kernel"]
    assert len(selected) == 1
    projected = [value for owner, value in calls if owner == "projector"]
    assert len(projected) == 1 and projected[0] is selected[0]
