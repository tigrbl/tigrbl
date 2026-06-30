from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp, TigrblRouter, op_alias, op_ctx
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, Integer
from tigrbl_base._base._op_base import OpBase
from tigrbl_concrete.system.docs.surface import op_surface
from tigrbl_core._spec.op_spec import OpSpec


async def _get(app: TigrblApp, path: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return await client.get(path)


def _get_path(app: TigrblApp, alias: str) -> str:
    for route in app.router.routes:
        if route.path.endswith(f"/{alias}") and "GET" in (route.methods or set()):
            return route.path
    raise AssertionError(f"GET route for {alias!r} not found")


@pytest.mark.asyncio
async def test_app_owned_op_ctx_materializes_to_rest_execution() -> None:
    class HealthApp(TigrblApp):
        TITLE = "health"
        VERSION = "1.0"
        LIFESPAN = None

        @op_ctx(alias="health", target="custom", http_methods=("GET",))
        def health(cls, ctx):
            return {"owner": cls.__name__, "ctx_type": type(ctx).__name__}

    app = HealthApp()
    response = await _get(app, _get_path(app, "health"))

    assert response.status_code == 200
    assert response.json()["owner"] == "HealthApp"
    assert response.json()["ctx_type"] in {"dict", "_Ctx"}
    assert HealthApp.ops.by_alias["health"][0].target == "custom"


@pytest.mark.asyncio
async def test_router_owned_op_ctx_materializes_after_app_include_router() -> None:
    class Widget(TableBase):
        __tablename__ = "router_scope_widgets"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias="router_health", target="custom", http_methods=("GET",))
        def router_health(cls, ctx):
            return {"owner": cls.__name__}

    router = TigrblRouter(prefix="/ops")
    router.include_table(Widget)
    app = TigrblApp()
    app.include_router(router)

    response = await _get(app, "/ops/widget/router_health")

    assert response.status_code == 200
    assert response.json() == {"owner": "Widget"}


@pytest.mark.asyncio
async def test_table_owned_op_ctx_materializes_through_include_table() -> None:
    class Widget(TableBase):
        __tablename__ = "op_surface_owner_widgets"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias="ping", target="custom", http_methods=("GET",))
        def ping(cls, ctx):
            return {"owner": cls.__name__}

    app = TigrblApp()
    app.include_table(Widget)

    response = await _get(app, "/widget/ping")

    assert response.status_code == 200
    assert response.json() == {"owner": "Widget"}


def test_op_surface_public_projection_covers_default_custom_and_base_contracts() -> None:
    default = OpSpec(alias="read", target="read", arity="member")
    custom = OpSpec(alias="export", target="custom", arity="collection")
    base = OpBase(alias="base_export", target="custom", arity="collection")

    assert op_surface(default)["family"] == "crud"
    assert op_surface(custom)["family"] == "custom"
    assert isinstance(base, OpSpec)
    assert base.alias == "base_export"


def test_op_extension_surface_declares_alias_ctx_and_op_ctx_specs() -> None:
    @op_alias(alias="health", target="custom", http_methods=("GET",))
    class Health(TableBase):
        __tablename__ = "op_extension_health"
        id = Column(Integer, primary_key=True)

        @op_ctx(alias="summary", target="custom", http_methods=("GET",), status_code=202)
        def summary(cls, ctx):
            return {"ok": True}

    aliases = {spec.alias: spec for spec in OpSpec.collect(Health)}

    assert aliases["health"].target == "custom"
    assert aliases["health"].http_methods == ("GET",)
    assert aliases["summary"].target == "custom"
    assert aliases["summary"].status_code == 202
