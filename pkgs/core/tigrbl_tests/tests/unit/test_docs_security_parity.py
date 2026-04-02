from __future__ import annotations

import asyncio

from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import HTTPBearer, TigrblApp
from tigrbl._spec import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.security import Security
from tigrbl.shortcuts.engine import mem


def _alpha_dep(cred=Security(HTTPBearer(scheme_name="AlphaToken"))):
    return cred


def _beta_dep(cred=Security(HTTPBearer(scheme_name="BetaToken"))):
    return cred


class Widget(TableBase, GUIDPk):
    __tablename__ = "widgets_docs_security_parity"

    name = Column(String, nullable=False)
    __tigrbl_ops__ = (
        OpSpec(alias="list", target="list"),
        OpSpec(alias="read", target="read", secdeps=(_alpha_dep,)),
        OpSpec(alias="create", target="create", secdeps=(_alpha_dep, _beta_dep)),
    )


def test_openapi_and_openrpc_security_are_derived_from_opspec_secdeps() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()

    async def _fetch() -> tuple[dict[str, object], dict[str, object]]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            openapi = (await client.get("/openapi.json")).json()
            openrpc = (await client.get("/openrpc.json")).json()
        return openapi, openrpc

    openapi, openrpc = asyncio.run(_fetch())

    read_security = openapi["paths"]["/widget/{item_id}"]["get"].get("security")
    create_security = openapi["paths"]["/widget"]["post"].get("security")
    assert read_security == [{"AlphaToken": []}]
    assert create_security == [{"AlphaToken": []}, {"BetaToken": []}]

    method_map = {method["name"]: method for method in openrpc["methods"]}
    assert method_map["Widget.list"].get("security") is None
    assert method_map["Widget.read"]["security"] == [{"AlphaToken": []}]
    assert method_map["Widget.create"]["security"] == [
        {"AlphaToken": []},
        {"BetaToken": []},
    ]

    openapi_schemes = openapi["components"]["securitySchemes"]
    openrpc_schemes = openrpc["components"]["securitySchemes"]
    assert set(openapi_schemes) >= {"AlphaToken", "BetaToken"}
    assert set(openrpc_schemes) >= {"AlphaToken", "BetaToken"}


def test_docs_ignore_router_security_dependency_metadata() -> None:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Widget)
    app.initialize()
    app.mount_jsonrpc()
    app.mount_openrpc()

    widget_router = app.routers["Widget"]
    for route in getattr(widget_router, "routes", []):
        try:
            object.__setattr__(route, "security_dependencies", [])
        except Exception:
            pass

    async def _fetch() -> tuple[dict[str, object], dict[str, object]]:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            openapi = (await client.get("/openapi.json")).json()
            openrpc = (await client.get("/openrpc.json")).json()
        return openapi, openrpc

    openapi, openrpc = asyncio.run(_fetch())

    assert openapi["paths"]["/widget"]["get"].get("security") is None
    assert openapi["paths"]["/widget/{item_id}"]["get"]["security"] == [
        {"AlphaToken": []}
    ]

    method_map = {method["name"]: method for method in openrpc["methods"]}
    assert method_map["Widget.list"].get("security") is None
    assert method_map["Widget.read"]["security"] == [{"AlphaToken": []}]
