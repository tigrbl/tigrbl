from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl_concrete._concrete._app import App as TigrblApp


async def _collect_asgi_messages(app: Any, scope: dict[str, Any]) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await app(scope, receive, send)
    return sent


@pytest.mark.asyncio
async def test_static_mount_serves_nested_files_with_inferred_content_type(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    nested = assets / "nested"
    nested.mkdir(parents=True)
    (nested / "hello.txt").write_text("hello-static", encoding="utf-8")
    app = TigrblApp(title="Static Contract")
    app.mount_static(directory=assets, path="/assets")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/assets/nested/hello.txt")

    assert response.status_code == 200
    assert response.text == "hello-static"
    assert response.headers["content-type"].startswith("text/plain")


@pytest.mark.asyncio
async def test_static_mount_returns_404_for_missing_files(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    app = TigrblApp(title="Static Missing Contract")
    app.mount_static(directory=assets, path="/assets")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/assets/missing.txt")

    assert response.status_code == 404
    assert response.text == "Not Found"


@pytest.mark.asyncio
async def test_static_mount_rejects_path_traversal_outside_mount_root(tmp_path: Path) -> None:
    assets = tmp_path / "assets"
    assets.mkdir()
    (tmp_path / "secret.txt").write_text("secret", encoding="utf-8")
    app = TigrblApp(title="Static Traversal Contract")
    app.mount_static(directory=assets, path="/assets")

    messages = await _collect_asgi_messages(
        app,
        {
            "type": "http",
            "method": "GET",
            "path": "/assets/../secret.txt",
            "query_string": b"",
            "headers": [],
        },
    )

    start = next(message for message in messages if message["type"] == "http.response.start")
    body = next(message for message in messages if message["type"] == "http.response.body")
    assert start["status"] == 404
    assert body["body"] == b"Not Found"
