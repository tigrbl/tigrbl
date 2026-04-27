from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_concrete._concrete._router import Router as TigrblRouter
from tigrbl_concrete.system import mount_asyncapi, mount_json_schema


@pytest.mark.asyncio
async def test_asyncapi_spec_is_mounted_without_promising_interactive_ui() -> None:
    app = TigrblApp(title="AsyncAPI Spec Only")
    router = TigrblRouter()

    @router.websocket("/ws/events", summary="Events socket")
    async def events(ws):
        await ws.accept()
        await ws.close()

    app.include_router(router)
    mount_asyncapi(app)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        spec = await client.get("/asyncapi.json")
        ui_candidates = [
            await client.get("/asyncapi"),
            await client.get("/asyncapi-ui"),
            await client.get("/asyncapi/docs"),
        ]

    assert spec.status_code == 200
    assert spec.json()["asyncapi"] == "2.6.0"
    assert "/ws/events" in spec.json()["channels"]
    assert [response.status_code for response in ui_candidates] == [404, 404, 404]


@pytest.mark.asyncio
async def test_json_schema_bundle_is_mounted_without_promising_interactive_ui() -> None:
    app = TigrblApp(title="JSON Schema Bundle Only")
    mount_json_schema(app)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        bundle = await client.get("/schemas.json")
        ui_candidates = [
            await client.get("/schemas"),
            await client.get("/schema-ui"),
            await client.get("/schemas/docs"),
        ]

    assert bundle.status_code == 200
    payload = bundle.json()
    assert payload["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert isinstance(payload["$defs"], dict)
    assert [response.status_code for response in ui_candidates] == [404, 404, 404]
