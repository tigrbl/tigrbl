from __future__ import annotations

from collections.abc import Iterator

import pytest
from httpx import ASGITransport, AsyncClient

from tigrbl import TigrblApp, op_ctx, resolver as _resolver
from tigrbl._spec import OpSpec
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase
from tigrbl.types import Column, Session, String


def _route_map(router) -> dict[str, tuple[str, set[str]]]:
    out: dict[str, tuple[str, set[str]]] = {}
    for route in getattr(router, "routes", []):
        name = getattr(route, "name", None)
        if not name or "." not in name:
            continue
        out[name.split(".", 1)[1]] = (
            str(getattr(route, "path", "")),
            set(getattr(route, "methods", set()) or set()),
        )
    return out


@pytest.fixture()
def custom_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "canonical_custom_op_widgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        @op_ctx(alias="echo", target="custom", arity="collection")
        def echo(cls, ctx):
            payload = dict(ctx.get("payload") or {})
            return {
                "message": payload.get("message"),
                "method": ctx.get("method"),
                "op": ctx.get("op"),
                "target": ctx.get("target"),
            }

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Widget)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, Widget, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_custom_op_projects_as_canonical_collection_route(custom_app_and_session) -> None:
    app, Widget, _ = custom_app_and_session

    routes = _route_map(app.core.Widget._model.rest.router)
    assert routes["echo"] == ("/widget/echo", {"POST"})

    spec = next(item for item in OpSpec.collect(Widget) if item.alias == "echo")
    assert spec.target == "custom"
    assert spec.arity == "collection"


@pytest.mark.asyncio
async def test_custom_op_executes_via_rpc_and_rest(custom_app_and_session) -> None:
    app, _, db = custom_app_and_session

    rpc_result = await app.rpc.Widget.echo({"message": "rpc"}, db=db)
    assert rpc_result == {
        "message": "rpc",
        "method": "echo",
        "op": "echo",
        "target": "custom",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post("/widget/echo", json={"message": "rest"})

    assert response.status_code == 200
    assert response.json() == {
        "message": "rest",
        "method": "POST",
        "op": "echo",
        "target": "custom",
    }
