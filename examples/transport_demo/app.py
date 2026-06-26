from __future__ import annotations

import json
import os
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
from tigrbl_core._spec import (
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    StreamFramingSpec,
    TextFramingSpec,
)


_JSONRPC_PROTOCOL_CLOSE_CODE = 1002


def _demo_db_path() -> Path:
    configured = os.environ.get("TIGRBL_TRANSPORT_DEMO_DB")
    if configured:
        return Path(configured)
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
            try:
                parsed = json.loads(raw)
            except Exception:
                return {"message": raw, "datagram": raw}
            if isinstance(parsed, dict):
                return parsed
    return {}


def _websocket_offered_subprotocols(ws: Any) -> tuple[str, ...]:
    scope = getattr(ws, "scope", {}) or {}
    declared = scope.get("subprotocols")
    if isinstance(declared, (list, tuple)):
        return tuple(str(item) for item in declared if str(item))
    headers = scope.get("headers")
    if isinstance(headers, dict):
        raw = str(headers.get("sec-websocket-protocol") or "")
        return tuple(token.strip() for token in raw.split(",") if token.strip())
    return ()


def _jsonrpc_error(
    request_id: Any,
    code: int,
    message: str,
    *,
    detail: str | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if detail:
        error["data"] = {"detail": detail}
    return {"jsonrpc": "2.0", "error": error, "id": request_id}


async def _send_jsonrpc_error(
    ws: Any,
    request_id: Any,
    code: int,
    message: str,
    *,
    detail: str | None = None,
) -> None:
    await ws.send_text(
        json.dumps(
            _jsonrpc_error(request_id, code, message, detail=detail),
            separators=(",", ":"),
        )
    )
    await ws.close(code=1000)


def build_fail_closed_examples() -> dict[str, str]:
    failures: dict[str, str] = {}
    try:
        WsBindingSpec(
            proto="wss",
            path="/wss/ndjson",
            framing=NdjsonFramingSpec(),
            subprotocols=("jsonrpc",),
        )
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
            framing=StreamFramingSpec(),
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
            framing=NdjsonFramingSpec(),
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

    @app.websocket("/ws/echo", proto="ws", framing=TextFramingSpec(), summary="WebSocket text echo")
    async def ws_echo(ws) -> None:
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"ws:{text}")
        await ws.close(code=1000)

    @app.websocket("/wss/echo", proto="wss", framing=TextFramingSpec(), summary="Secure WebSocket text echo")
    async def wss_echo(ws) -> None:
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"wss:{text}")
        await ws.close(code=1000)

    @app.websocket(
        "/wss/jsonrpc",
        proto="wss",
        framing=JsonRpcFramingSpec(),
        subprotocols=("jsonrpc",),
        summary="Secure WebSocket JSON-RPC echo",
    )
    async def wss_jsonrpc(ws) -> None:
        if "jsonrpc" not in _websocket_offered_subprotocols(ws):
            await ws.close(code=_JSONRPC_PROTOCOL_CLOSE_CODE)
            return
        await ws.accept(subprotocol="jsonrpc")
        try:
            text = await ws.receive_text()
        except RuntimeError:
            await ws.close(code=1000)
            return
        try:
            request = json.loads(text or "")
        except Exception:
            await ws.close(code=_JSONRPC_PROTOCOL_CLOSE_CODE)
            return
        if not isinstance(request, dict):
            await _send_jsonrpc_error(
                ws,
                None,
                -32600,
                "Invalid Request",
                detail="JSON-RPC request must be an object.",
            )
            return
        request_id = request.get("id")
        if request.get("jsonrpc") != "2.0":
            await _send_jsonrpc_error(
                ws,
                request_id,
                -32600,
                "Invalid Request",
                detail="jsonrpc must equal '2.0'.",
            )
            return
        if "id" not in request:
            await _send_jsonrpc_error(
                ws,
                None,
                -32600,
                "Invalid Request",
                detail="id is required for the demo request-response rail.",
            )
            return
        method = request.get("method")
        if method != "demo.echo":
            await _send_jsonrpc_error(
                ws,
                request_id,
                -32601,
                "Method not found",
                detail="Only demo.echo is supported on this demo rail.",
            )
            return
        params = request.get("params")
        if params is not None and not isinstance(params, dict):
            await _send_jsonrpc_error(
                ws,
                request_id,
                -32602,
                "Invalid params",
                detail="params must be an object when present.",
            )
            return
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "method": method,
                "params": params,
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
