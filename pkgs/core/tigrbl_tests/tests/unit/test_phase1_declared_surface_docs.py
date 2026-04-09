from __future__ import annotations

from httpx import ASGITransport, Client
from sqlalchemy import Column, String

from tigrbl import TableBase, TigrblApp, hook_ctx, stream_ctx, websocket_ctx
from tigrbl.orm.mixins import GUIDPk
from tigrbl.shortcuts.engine import mem


def _build_app():
    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets_phase1_surface"
        name = Column(String, nullable=False)

        @stream_ctx(
            "/widget/events",
            alias="events",
            exchange="server_stream",
            tx_scope="read_only",
            subevents=("chunk",),
            rest=True,
        )
        def events(cls, ctx):
            return ctx

        @websocket_ctx(
            "/widget/ws",
            alias="socket_rpc",
            framing="jsonrpc",
            tx_scope="read_write",
        )
        def socket_rpc(cls, ctx):
            return ctx

        @hook_ctx(
            ops="events",
            phase="PRE_HANDLER",
            exchange="server_stream",
            bindings=("http.stream",),
            family=("custom",),
            subevents=("chunk",),
        )
        def event_hook(cls, ctx):
            ctx["seen"] = True

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    return app, Widget


def test_declared_hook_selectors_filter_matching_op() -> None:
    _, model = _build_app()
    hooks = model.hooks.events.PRE_HANDLER
    assert len(hooks) == 1


def test_openapi_uses_declared_surface_metadata() -> None:
    app, _ = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openapi.json").json()

    operation = payload["paths"]["/widget/events"]["get"]
    assert operation["x-tigrbl-surface"]["binding"]["proto"] == "http.stream"
    assert operation["x-tigrbl-surface"]["binding"]["family"] == "stream"
    assert operation["x-tigrbl-surface"]["binding"]["framing"] == "stream"
    assert operation["x-tigrbl-surface"]["exchange"] == "server_stream"
    assert operation["x-tigrbl-surface"]["family"] == "custom"
    assert operation["x-tigrbl-surface"]["subevents"] == ["chunk"]
    assert operation["x-tigrbl-surface"]["txScope"] == "read_only"


def test_openrpc_uses_declared_surface_metadata_and_ws_jsonrpc_bridge() -> None:
    app, model = _build_app()
    transport = ASGITransport(app=app)

    with Client(transport=transport, base_url="http://test") as client:
        payload = client.get("/openrpc.json").json()

    methods = {method["name"]: method for method in payload["methods"]}
    socket_method = methods[f"{model.__name__}.socket_rpc"]
    bindings = socket_method["x-tigrbl-surface"]["bindings"]
    assert any(
        binding["proto"] == "ws"
        and binding["framing"] == "jsonrpc"
        and binding["family"] == "socket"
        for binding in bindings
    )
    assert socket_method["x-tigrbl-surface"]["family"] == "custom"
    assert socket_method["x-tigrbl-surface"]["txScope"] == "read_write"

    socket_ops = model.ops.by_alias["socket_rpc"]
    assert any(getattr(binding, "proto", None) == "http.jsonrpc" for binding in socket_ops[0].bindings)
