from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_concrete._concrete._router import Router as TigrblRouter
from tigrbl_concrete.system import mount_json_schema
import tigrbl_concrete.system as system_helpers
import tigrbl_concrete.system.docs as docs_helpers
from tigrbl_core._spec.docs_spec import DocsPayloadSpec, DocsProjectionSpec


@pytest.mark.asyncio
async def test_asyncapi_spec_and_ui_are_not_supported() -> None:
    app = TigrblApp(title="AsyncAPI Spec Only")
    router = TigrblRouter()

    @router.websocket("/ws/events", summary="Events socket")
    async def events(ws):
        await ws.accept()
        await ws.close()

    app.include_router(router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        spec = await client.get("/asyncapi.json")
        ui_candidates = [
            await client.get("/asyncapi"),
            await client.get("/asyncapi-ui"),
            await client.get("/asyncapi/docs"),
        ]

    assert spec.status_code == 404
    assert [response.status_code for response in ui_candidates] == [404, 404, 404]


def test_asyncapi_helpers_are_not_exported() -> None:
    for helper in ("mount_asyncapi", "build_asyncapi_spec"):
        assert helper not in getattr(system_helpers, "__all__", ())
        assert helper not in getattr(docs_helpers, "__all__", ())
        assert not hasattr(system_helpers, helper)
        assert not hasattr(docs_helpers, helper)


def test_asyncapi_docs_payload_kind_is_rejected() -> None:
    projection = DocsProjectionSpec(name="public")

    with pytest.raises(ValueError, match="AsyncAPI docs payloads are not supported"):
        DocsPayloadSpec(kind="asyncapi", projection=projection)  # type: ignore[arg-type]


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
