from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl_concrete._concrete._event_stream_response import EventStreamResponse
from tigrbl_concrete._concrete._request import Request
from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete._concrete._streaming_response import StreamingResponse
from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_concrete._concrete._router import Router as TigrblRouter
from tigrbl_concrete.system import mount_asyncapi, mount_json_schema, mount_lens, mount_openapi, mount_openrpc, mount_static, mount_swagger


async def _collect_asgi_messages(app: Any, scope: dict[str, Any], inbound: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []
    pending = list(inbound or [])

    async def receive() -> dict[str, Any]:
        if pending:
            return pending.pop(0)
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


@pytest.mark.asyncio
async def test_docs_surfaces_include_json_schema_and_asyncapi_specs_and_static_mount(tmp_path: Path) -> None:
    app = TigrblApp(title="Phase 7 Docs")
    router = TigrblRouter()
    mount_openapi(app)
    mount_swagger(app)
    mount_openrpc(app)
    mount_lens(app)
    mount_json_schema(app)
    mount_asyncapi(app)

    @router.websocket("/ws/echo", summary="Echo socket")
    async def echo_socket(ws):
        await ws.accept()
        await ws.close()

    app.include_router(router)

    assets = tmp_path / "assets"
    nested = assets / "nested"
    nested.mkdir(parents=True)
    (nested / "hello.txt").write_text("hello-static", encoding="utf-8")
    app.mount_static(directory=assets, path="/assets")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        openapi_res = await client.get("/openapi.json")
        swagger_res = await client.get("/docs")
        openrpc_res = await client.get("/openrpc.json")
        lens_res = await client.get("/lens")
        schemas_res = await client.get("/schemas.json")
        asyncapi_res = await client.get("/asyncapi.json")
        static_res = await client.get("/assets/nested/hello.txt")

    assert openapi_res.status_code == 200
    assert swagger_res.status_code == 200
    assert openrpc_res.status_code == 200
    assert lens_res.status_code == 200
    assert schemas_res.status_code == 200
    assert asyncapi_res.status_code == 200
    assert static_res.status_code == 200
    assert static_res.text == "hello-static"

    assert openapi_res.json()["openapi"] == "3.1.0"
    assert schemas_res.json()["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert isinstance(schemas_res.json()["$defs"], dict)
    assert asyncapi_res.json()["asyncapi"] == "2.6.0"
    assert "/ws/echo" in asyncapi_res.json()["channels"]
    assert "swagger" in swagger_res.text.lower()
    assert "openrpc" in lens_res.text.lower()


@pytest.mark.asyncio
async def test_cookie_form_and_upload_surfaces_roundtrip() -> None:
    app = TigrblApp(title="Phase 7 Forms")
    router = TigrblRouter()

    @router.get("/cookie/set")
    def set_cookie() -> Response:
        response = Response.text("ok")
        response.set_cookie("sid", "abc123")
        return response

    @router.get("/cookie/read")
    def read_cookie(request: Request) -> dict[str, str | None]:
        return {"sid": request.cookies.get("sid")}

    @router.post("/form")
    async def read_form(request: Request) -> dict[str, Any]:
        form = await request.form()
        avatar = request.files.get("avatar")
        if isinstance(avatar, list):
            avatar = avatar[0]
        return {
            "name": form.get("name"),
            "city": form.get("city"),
            "avatar_name": getattr(avatar, "filename", None),
            "avatar_type": getattr(avatar, "content_type", None),
            "avatar_text": avatar.text() if avatar else None,
        }

    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get("/cookie/set")
        cookie_res = await client.get("/cookie/read")
        form_res = await client.post(
            "/form",
            data={"name": "alice", "city": "dallas"},
            files={"avatar": ("avatar.txt", b"hello-upload", "text/plain")},
        )

    assert cookie_res.status_code == 200
    assert cookie_res.json() == {"sid": "abc123"}
    assert form_res.status_code == 200
    assert form_res.json() == {
        "name": "alice",
        "city": "dallas",
        "avatar_name": "avatar.txt",
        "avatar_type": "text/plain",
        "avatar_text": "hello-upload",
    }


@pytest.mark.asyncio
async def test_streaming_and_sse_surfaces_emit_multiple_asgi_body_messages() -> None:
    app = TigrblApp(title="Phase 7 Streams")
    router = TigrblRouter()

    @router.get("/stream")
    def stream() -> StreamingResponse:
        return StreamingResponse([b"a", b"b", b"c"], media_type="text/plain")

    @router.get("/events")
    def events() -> EventStreamResponse:
        return EventStreamResponse([
            {"event": "message", "data": {"ok": True}},
            "done",
        ])

    app.include_router(router)

    stream_messages = await _collect_asgi_messages(
        app,
        {"type": "http", "method": "GET", "path": "/stream", "query_string": b"", "headers": []},
    )
    sse_messages = await _collect_asgi_messages(
        app,
        {"type": "http", "method": "GET", "path": "/events", "query_string": b"", "headers": []},
    )

    stream_bodies = [m for m in stream_messages if m["type"] == "http.response.body"]
    assert len(stream_bodies) == 4
    assert stream_bodies[0]["body"] == b"a"
    assert stream_bodies[1]["body"] == b"b"
    assert stream_bodies[2]["body"] == b"c"
    assert stream_bodies[3]["body"] == b""
    assert stream_bodies[2]["more_body"] is True
    assert stream_bodies[3]["more_body"] is False

    sse_start = next(m for m in sse_messages if m["type"] == "http.response.start")
    sse_bodies = [m for m in sse_messages if m["type"] == "http.response.body"]
    assert dict(sse_start["headers"])[b"content-type"].startswith(b"text/event-stream")
    assert len(sse_bodies) == 3
    assert b"event: message" in sse_bodies[0]["body"]
    assert b'data: {"ok":true}' in sse_bodies[0]["body"]
    assert b"data: done" in sse_bodies[1]["body"]
    assert sse_bodies[-1]["more_body"] is False


@pytest.mark.asyncio
async def test_websocket_surface_accepts_receives_and_sends_text() -> None:
    app = TigrblApp(title="Phase 7 WS")
    router = TigrblRouter()

    @router.websocket("/ws/echo")
    async def echo(ws):
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(f"echo:{text}")
        await ws.close()

    app.include_router(router)

    sent: list[dict[str, Any]] = []
    pending = [
        {"type": "websocket.receive", "text": "hi"},
    ]

    async def receive() -> dict[str, Any]:
        return pending.pop(0) if pending else {"type": "websocket.disconnect", "code": 1000}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app({"type": "websocket", "path": "/ws/echo", "query_string": b"", "headers": []}, receive, send)

    assert sent[0]["type"] == "websocket.accept"
    assert sent[1] == {"type": "websocket.send", "text": "echo:hi"}
    assert sent[2]["type"] == "websocket.close"


def test_websocket_routes_register_concrete_bindings_with_prefixed_paths() -> None:
    app = TigrblApp(title="Phase 7 WS Prefix")
    router = TigrblRouter()

    @router.websocket("/echo", framing="jsonrpc")
    async def echo(ws):
        await ws.accept()
        await ws.close()

    app.include_router(router, prefix="/ws")

    system_model = app.tables["__tigrbl_system_routes__"]
    spec = next(
        item
        for item in tuple(getattr(getattr(system_model, "ops", None), "all", ()) or ())
        if getattr(item, "alias", None) == "echo"
    )
    binding = spec.bindings[0]

    assert binding.path == "/ws/echo"
    assert binding.exchange == "bidirectional_stream"
    assert binding.framing == "jsonrpc"
