from __future__ import annotations

from inspect import isawaitable
from typing import Any
import uuid

import httpx
import pytest

from tigrbl import TigrblApp, TigrblRouter, op_ctx
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import BaseModel, Column, String

from .uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server


class TokenInventorySchema(BaseModel):
    access_tokens: int
    refresh_tokens: int


def _payload() -> dict[str, int]:
    return {"access_tokens": 3, "refresh_tokens": 1}


def _table_name(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


async def _initialize(app: TigrblApp) -> None:
    result = app.initialize()
    if isawaitable(result):
        await result


async def _post_via_uvicorn(app: TigrblApp, path: str) -> httpx.Response:
    base_url, server, task = await run_uvicorn_in_task(app)
    try:
        async with httpx.AsyncClient() as client:
            return await client.post(f"{base_url}{path}", json={})
    finally:
        await stop_uvicorn_server(server, task)


def _operation_paths(app: TigrblApp) -> set[str]:
    return {getattr(route, "path", "") for route in getattr(app, "routes", ())}


def _route_ops(app: TigrblApp) -> tuple[Any, ...]:
    route_model = app.tables["__tigrbl_route_ops__"]
    return tuple(getattr(getattr(route_model, "ops", None), "all", ()) or ())


def _model_op(app: TigrblApp, model_name: str, alias: str) -> Any:
    model = app.tables[model_name]
    return next(
        spec
        for spec in tuple(getattr(getattr(model, "ops", None), "all", ()) or ())
        if getattr(spec, "alias", "") == alias
    )


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_table_owned_op_ctx_materializes_through_include_table_and_executes_under_uvicorn() -> None:
    TableBase.metadata.clear()

    class Inventory(TableBase, GUIDPk):
        __tablename__ = _table_name("owner_scope_table_inventory")
        __resource__ = "inventory"
        name = Column(String)

        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity="collection",
            response_schema=TokenInventorySchema,
            persist="skip",
        )
        def token_inventory(cls, ctx):
            return _payload()

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Inventory, prefix="")
    await _initialize(app)

    assert "/inventory/token_inventory" in _operation_paths(app)
    assert "/inventory/token_inventory" in app.openapi()["paths"]
    assert "TokenInventorySchema" in app.openapi()["components"]["schemas"]

    response = await _post_via_uvicorn(app, "/inventory/token_inventory")

    assert response.status_code == 200
    assert response.json() == _payload()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_router_owned_projection_preserves_table_op_ctx_semantics_and_mount_prefix() -> None:
    TableBase.metadata.clear()

    class Inventory(TableBase, GUIDPk):
        __tablename__ = _table_name("owner_scope_router_inventory")
        __resource__ = "inventory"
        name = Column(String)

        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity="collection",
            response_schema=TokenInventorySchema,
            persist="skip",
        )
        def token_inventory(cls, ctx):
            return _payload()

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Inventory, prefix="")
    router_init = router.initialize()
    if isawaitable(router_init):
        await router_init

    app = TigrblApp(engine=mem(async_=False))
    app.include_router(router, prefix="/tenant")
    await _initialize(app)

    token_op = _model_op(app, "Inventory", "token_inventory")
    binding = token_op.bindings[0]

    assert "/tenant/inventory/token_inventory" in _operation_paths(app)
    assert binding.path == "/tenant/inventory/token_inventory"
    assert token_op.response_model is TokenInventorySchema
    assert token_op.persist == "skip"

    response = await _post_via_uvicorn(app, "/tenant/inventory/token_inventory")

    assert response.status_code == 200
    assert response.json() == _payload()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_app_local_op_ctx_materializes_without_table_owner_and_executes_under_uvicorn() -> None:
    TableBase.metadata.clear()

    class InventoryApp(TigrblApp):
        @op_ctx(
            alias="token_inventory",
            target="custom",
            arity="collection",
            response_schema=TokenInventorySchema,
            persist="skip",
        )
        def token_inventory(cls, ctx):
            return _payload()

    app = InventoryApp(engine=mem(async_=False))
    await _initialize(app)

    token_op = _model_op(app, "InventoryApp", "token_inventory")

    assert "/inventoryapp/token_inventory" in _operation_paths(app)
    assert "/inventoryapp/token_inventory" in app.openapi()["paths"]
    assert token_op.table is InventoryApp
    assert token_op.response_model is TokenInventorySchema

    response = await _post_via_uvicorn(app, "/inventoryapp/token_inventory")

    assert response.status_code == 200
    assert response.json() == _payload()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_owner_scope_member_arity_uses_member_route_shape_across_table_router_and_app() -> None:
    TableBase.metadata.clear()

    class TableScoped(TableBase, GUIDPk):
        __tablename__ = _table_name("owner_scope_member_table")
        __resource__ = "table_inventory"
        name = Column(String)

        @op_ctx(alias="inspect", target="custom", arity="member", persist="skip")
        def inspect(cls, ctx):
            return {"scope": "table"}

    class RouterScoped(TableBase, GUIDPk):
        __tablename__ = _table_name("owner_scope_member_router")
        __resource__ = "router_inventory"
        name = Column(String)

        @op_ctx(alias="inspect", target="custom", arity="member", persist="skip")
        def inspect(cls, ctx):
            return {"scope": "router"}

    class AppScoped(TigrblApp):
        @op_ctx(alias="inspect", target="custom", arity="member", persist="skip")
        def inspect(cls, ctx):
            return {"scope": "app"}

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(RouterScoped, prefix="")
    router_init = router.initialize()
    if isawaitable(router_init):
        await router_init

    app = AppScoped(engine=mem(async_=False))
    app.include_table(TableScoped, prefix="")
    app.include_router(router, prefix="/mounted")
    await _initialize(app)

    paths = _operation_paths(app)

    assert "/table_inventory/{item_id}/inspect" in paths
    assert "/mounted/router_inventory/{item_id}/inspect" in paths
    assert "/appscoped/{item_id}/inspect" in paths
