from __future__ import annotations

import json

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import Column, Integer, String

from tigrbl import TableBase, TigrblApp
from tigrbl.factories.engine import mem
from tigrbl.system import (
    build_openapi,
    build_openrpc_spec,
    mount_lens,
    mount_openapi,
    mount_openrpc,
    mount_swagger,
)


class DocsMountParityWidget(TableBase):
    __tablename__ = "docs_mount_parity_widgets_contract"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


def _build_docs_app() -> TigrblApp:
    app = TigrblApp(engine=mem(async_=False), mount_system=False)
    app.include_table(DocsMountParityWidget)
    app.initialize()
    app.mount_jsonrpc(prefix="/rpc")
    mount_openapi(app, path="/custom/openapi.json", name="contract_openapi")
    mount_openrpc(app, path="/custom/openrpc.json", name="contract_openrpc")
    mount_swagger(app, path="/custom/docs", name="contract_swagger")
    mount_lens(
        app,
        path="/custom/lens",
        name="contract_lens",
        spec_path="/custom/openrpc.json",
    )
    return app


def _json_normalized(value: object) -> object:
    return json.loads(json.dumps(value))


@pytest.mark.asyncio
async def test_mounted_docs_json_matches_direct_runtime_builders() -> None:
    app = _build_docs_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        openapi_response = await client.get("/custom/openapi.json")
        openrpc_response = await client.get("/custom/openrpc.json")

    assert openapi_response.status_code == 200
    assert openapi_response.json() == _json_normalized(
        build_openapi(
            app,
            docs_path="/custom/openapi.json",
        )
    )

    assert openrpc_response.status_code == 200
    assert openrpc_response.json() == _json_normalized(
        build_openrpc_spec(
            app,
            docs_path="/custom/openrpc.json",
        )
    )


@pytest.mark.asyncio
async def test_mounted_docs_ui_surfaces_reference_mounted_json_paths() -> None:
    app = _build_docs_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        swagger_response = await client.get("/custom/docs")
        lens_response = await client.get("/custom/lens")

    assert swagger_response.status_code == 200
    assert 'url: "/custom/openapi.json"' in swagger_response.text

    assert lens_response.status_code == 200
    assert "/custom/openapi.json" in lens_response.text
    assert "/custom/openrpc.json" in lens_response.text
