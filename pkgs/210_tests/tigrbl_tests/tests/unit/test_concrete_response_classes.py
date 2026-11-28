from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp
from tigrbl import rpc_call
from tigrbl_concrete._concrete._file_response import FileResponse
from tigrbl_concrete._concrete._html_response import HTMLResponse
from tigrbl_concrete._concrete._json_response import JSONResponse
from tigrbl_concrete._concrete._plain_text_response import PlainTextResponse
from tigrbl_concrete._concrete._redirect_response import RedirectResponse
from tigrbl_concrete._concrete._response import Response

from .response_utils import build_model_for_response


def test_response_base_non_stream_asgi_send_and_cookie_state() -> None:
    sent: list[dict[str, object]] = []

    async def _send(message: dict[str, object]) -> None:
        sent.append(message)

    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    response = Response.json({"ok": True}, status_code=201, headers={"X-Test": "1"})
    response.set_cookie("session", "abc123", httponly=True)

    scope = {"type": "http", "method": "GET", "path": "/", "headers": []}
    asyncio.run(response(scope, _receive, _send))

    assert response.status_line() == "201 Created"
    assert response.json_body() == {"ok": True}
    assert response.cookies.get("session") == "abc123"
    assert len(sent) == 2
    assert sent[0]["type"] == "http.response.start"
    assert sent[0]["status"] == 201
    start_headers = dict(sent[0]["headers"])
    assert start_headers[b"x-test"] == b"1"
    assert b"set-cookie" in start_headers
    assert sent[1] == {"type": "http.response.body", "body": b'{"ok":true}', "more_body": False}


def test_json_html_and_plain_text_response_classes_are_first_class() -> None:
    json_response = JSONResponse({"ok": True}, status_code=202, headers={"X-Json": "1"})
    assert json_response.status_code == 202
    assert json_response.media_type == "application/json"
    assert json_response.json_body() == {"ok": True}
    assert json_response.headers_map.get("x-json") == "1"

    html_response = HTMLResponse("<h1>pong</h1>", headers={"X-Html": "1"})
    assert html_response.body_text == "<h1>pong</h1>"
    assert html_response.headers_map.get("content-type") == "text/html; charset=utf-8"
    assert html_response.headers_map.get("x-html") == "1"

    text_response = PlainTextResponse("pong", headers={"X-Text": "1"})
    assert text_response.body_text == "pong"
    assert text_response.headers_map.get("content-type") == "text/plain; charset=utf-8"
    assert text_response.headers_map.get("x-text") == "1"


def test_file_response_supports_override_headers_and_download_metadata(tmp_path) -> None:
    file_path = tmp_path / "payload.txt"
    file_path.write_text("payload")

    response = FileResponse(
        str(file_path),
        status_code=206,
        headers={"X-File": "1"},
        filename="download.txt",
        download=True,
    )

    assert response.status_code == 206
    assert response.body == b"payload"
    assert response.media_type == "text/plain"
    assert response.headers_map.get("x-file") == "1"
    assert response.headers_map.get("content-disposition") == 'attachment; filename="download.txt"'


def test_redirect_response_defaults_and_headers() -> None:
    response = RedirectResponse("/redirected", headers={"X-Redirect": "1"})

    assert response.status_code == 307
    assert response.url == "/redirected"
    assert response.body == b""
    assert response.headers_map.get("location") == "/redirected"
    assert response.headers_map.get("x-redirect") == "1"


@pytest.mark.asyncio
async def test_json_response_rest_and_rpc_parity(tmp_path) -> None:
    widget, _ = build_model_for_response("json", tmp_path)
    app = TigrblApp()
    app.include_router(widget.rest.router)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rest_response = await client.post("/widget/download", json={})
    rpc_result = await rpc_call(SimpleNamespace(tables={"Widget": widget}), widget, "download", {}, db=SimpleNamespace())

    assert rest_response.status_code == 200
    assert rest_response.headers["content-type"].startswith("application/json")
    assert rest_response.json() == {"pong": True}
    assert rpc_result["status_code"] == 200
    assert rpc_result["body"] == b'{"pong":true}'


@pytest.mark.asyncio
async def test_html_response_rest_and_rpc_parity(tmp_path) -> None:
    widget, _ = build_model_for_response("html", tmp_path)
    app = TigrblApp()
    app.include_router(widget.rest.router)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rest_response = await client.post("/widget/download", json={})
    rpc_result = await rpc_call(SimpleNamespace(tables={"Widget": widget}), widget, "download", {}, db=SimpleNamespace())

    assert rest_response.text == "<h1>pong</h1>"
    assert rest_response.headers["content-type"].startswith("text/html")
    assert rpc_result["body"] == b"<h1>pong</h1>"


@pytest.mark.asyncio
async def test_plain_text_response_rest_and_rpc_parity(tmp_path) -> None:
    widget, _ = build_model_for_response("text", tmp_path)
    app = TigrblApp()
    app.include_router(widget.rest.router)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        rest_response = await client.post("/widget/download", json={})
    rpc_result = await rpc_call(SimpleNamespace(tables={"Widget": widget}), widget, "download", {}, db=SimpleNamespace())

    assert rest_response.text == "pong"
    assert rest_response.headers["content-type"].startswith("text/plain")
    assert rpc_result["body"] == b"pong"


@pytest.mark.asyncio
async def test_redirect_response_rest_and_rpc_parity(tmp_path) -> None:
    widget, _ = build_model_for_response("redirect", tmp_path)
    app = TigrblApp()
    app.include_router(widget.rest.router)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as client:
        rest_response = await client.post("/widget/download", json={})
    rpc_result = await rpc_call(SimpleNamespace(tables={"Widget": widget}), widget, "download", {}, db=SimpleNamespace())

    assert rest_response.status_code == 307
    assert rest_response.headers["location"] == "/redirected"
    assert rest_response.content == b""
    assert rpc_result["status_code"] == 307
    assert dict(rpc_result["headers"])["location"] == "/redirected"
