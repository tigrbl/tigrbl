from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tigrbl import (
    EventStreamResponse,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    MutualTLS,
    OpSpec,
    Request,
    SseBindingSpec,
    StreamingResponse,
    TableBase,
    TigrblApp,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl.factories.engine import sqlitef
from tigrbl.security import Security
from tigrbl.types import Column, Integer, String


def _demo_db_path() -> Path:
    return Path(__file__).with_name("transport_demo.sqlite3")


def _raw_stream_chunks() -> tuple[bytes, ...]:
    return (
        b"alpha\n",
        b"beta\n",
        b"gamma\n",
    )


def _ndjson_stream_chunks() -> tuple[bytes, ...]:
    return tuple(
        json.dumps(
            {"kind": "stream", "index": idx, "transport": "ndjson"},
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
        for idx in range(3)
    )


def _sse_events() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "event": "demo",
            "id": idx + 1,
            "data": {"index": idx, "transport": "sse"},
        }
        for idx in range(3)
    )


def _mtls_dep(
    cred=Security(
        MutualTLS(
            scheme_name="MutualTLSAuth",
            description="Mutual TLS client certificate",
        )
    ),
):
    return cred


class DemoItem(TableBase):
    __tablename__ = "transport_demo_item"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    __tigrbl_ops__ = (
        OpSpec(
            alias="DemoItem.create",
            target="create",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("POST",),
                    path="/items",
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="DemoItem.create",
                    endpoint="/rpc",
                ),
            ),
        ),
        OpSpec(
            alias="DemoItem.read",
            target="read",
            bindings=(
                HttpRestBindingSpec(
                    proto="http.rest",
                    methods=("GET",),
                    path="/items/{id}",
                ),
                HttpJsonRpcBindingSpec(
                    proto="http.jsonrpc",
                    rpc_method="DemoItem.read",
                    endpoint="/rpc",
                ),
            ),
        ),
    )


def _decode_ctx_payload(ctx: Any) -> dict[str, Any]:
    getter = getattr(ctx, "get", None)
    body = getter("body") if callable(getter) else None
    if isinstance(body, bytearray):
        body = bytes(body)
    if isinstance(body, bytes):
        raw = body.decode("utf-8").strip()
        if raw:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return parsed
    return {}


def build_fail_closed_examples() -> dict[str, str]:
    failures: dict[str, str] = {}
    try:
        WsBindingSpec(proto="wss", path="/wss/ndjson", framing="ndjson")
    except ValueError as exc:
        failures["wss_ndjson"] = str(exc)
    return failures


def build_demo_matrix() -> list[dict[str, str]]:
    return [
        {
            "demo": "h1-h2-h3-profiles",
            "surface": "operator profiles",
            "entrypoint": "examples/transport_demo/app.py:build_app",
        },
        {
            "demo": "rest-and-jsonrpc",
            "surface": "/items and /rpc",
            "entrypoint": "DemoItem",
        },
        {
            "demo": "stream",
            "surface": "/stream/raw",
            "entrypoint": "HttpStreamBindingSpec(stream)",
        },
        {
            "demo": "stream-ndjson",
            "surface": "/stream/ndjson",
            "entrypoint": "HttpStreamBindingSpec(ndjson)",
        },
        {
            "demo": "sse",
            "surface": "/sse/events",
            "entrypoint": "SseBindingSpec",
        },
        {
            "demo": "websocket-ws-wss",
            "surface": "/ws/echo and /wss/echo",
            "entrypoint": "WsBindingSpec(text)",
        },
        {
            "demo": "wss-jsonrpc",
            "surface": "/wss/jsonrpc",
            "entrypoint": "WsBindingSpec(jsonrpc)",
        },
        {
            "demo": "mtls",
            "surface": "/mtls/echo",
            "entrypoint": "MutualTLS",
        },
        {
            "demo": "webtransport-session",
            "surface": "/transport/session",
            "entrypoint": "WebTransportBindingSpec",
        },
    ]


def build_app(db_path: str | Path | None = None) -> TigrblApp:
    path = Path(db_path) if db_path is not None else _demo_db_path()
    app = TigrblApp(
        title="Tigrbl Transport Demo",
        version="0.1.0",
        description="Repo-owned transport demo matrix for REST, JSON-RPC, stream, SSE, websocket, mTLS, and WebTransport surfaces.",
        engine=sqlitef(str(path), async_=False),
        mount_system=False,
    )
    app.include_table(DemoItem)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    app.mount_openapi(path="/openapi.json")
    app.mount_openrpc(path="/openrpc.json")
    app.mount_asyncapi(path="/asyncapi.json")

    @app.get("/matrix")
    def demo_matrix() -> dict[str, Any]:
        return {
            "demos": build_demo_matrix(),
            "negative_examples": build_fail_closed_examples(),
        }

    def raw_stream() -> StreamingResponse:
        return StreamingResponse(_raw_stream_chunks(), media_type="application/octet-stream")

    app.add_route(
        "/stream/raw",
        raw_stream,
        methods=("GET",),
        summary="Generic byte stream demo",
        tigrbl_binding=HttpStreamBindingSpec(
            proto="http.stream",
            path="/stream/raw",
            methods=("GET",),
            framing="stream",
        ),
        tigrbl_exchange="server_stream",
    )

    def ndjson_stream() -> StreamingResponse:
        return StreamingResponse(_ndjson_stream_chunks(), media_type="application/x-ndjson")

    app.add_route(
        "/stream/ndjson",
        ndjson_stream,
        methods=("GET",),
        summary="NDJSON stream demo",
        tigrbl_binding=HttpStreamBindingSpec(
            proto="http.stream",
            path="/stream/ndjson",
            methods=("GET",),
            framing="ndjson",
        ),
        tigrbl_exchange="server_stream",
    )

    def sse_events() -> EventStreamResponse:
        return EventStreamResponse(_sse_events())

    app.add_route(
        "/sse/events",
        sse_events,
        methods=("GET",),
        summary="Server-sent events demo",
        tigrbl_binding=SseBindingSpec(
            proto="http.sse",
            path="/sse/events",
            methods=("GET",),
        ),
        tigrbl_exchange="event_stream",
    )

    @app.websocket("/ws/echo", proto="ws", framing="text", summary="WebSocket text echo")
    async def ws_echo(ws) -> None:
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"ws:{text}")
        await ws.close(code=1000)

    @app.websocket("/wss/echo", proto="wss", framing="text", summary="Secure WebSocket text echo")
    async def wss_echo(ws) -> None:
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"wss:{text}")
        await ws.close(code=1000)

    @app.websocket(
        "/wss/jsonrpc",
        proto="wss",
        framing="jsonrpc",
        subprotocols=("jsonrpc",),
        summary="Secure WebSocket JSON-RPC echo",
    )
    async def wss_jsonrpc(ws) -> None:
        await ws.accept()
        text = await ws.receive_text()
        request = json.loads(text or "{}")
        payload = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "method": request.get("method"),
                "params": request.get("params"),
                "transport": "wss-jsonrpc",
            },
        }
        await ws.send_text(json.dumps(payload, separators=(",", ":")))
        await ws.close(code=1000)

    @app.get(
        "/mtls/echo",
        security_dependencies=[_mtls_dep],
        summary="mTLS protected echo",
    )
    def mtls_echo(request: Request) -> dict[str, Any]:
        return {
            "ok": True,
            "path": request.scope.get("path"),
            "scheme": request.scope.get("scheme"),
            "security": "mutualTLS",
        }

    async def webtransport_session(ctx: Any) -> dict[str, Any]:
        payload = _decode_ctx_payload(ctx)
        return {
            "session": "single",
            "transport": "webtransport",
            "framing": "webtransport",
            "unidirectional_streams": [
                {"id": "uni-1", "direction": "server-send", "message": "demo-unidirectional"}
            ],
            "bidirectional_streams": [
                {
                    "id": "bidi-1",
                    "direction": "bidirectional",
                    "message": payload.get("message", "demo-bidirectional"),
                }
            ],
            "datagrams": [
                {"direction": "client-to-server", "payload": payload.get("datagram", "ping")},
                {"direction": "server-to-client", "payload": "pong"},
            ],
        }

    app.add_route(
        "/transport/session",
        webtransport_session,
        methods=("POST",),
        summary="Provisional WebTransport session demo",
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/transport/session",
        ),
        tigrbl_exchange="bidirectional_stream",
    )

    return app


app = build_app()
