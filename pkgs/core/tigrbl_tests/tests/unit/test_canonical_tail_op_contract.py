from __future__ import annotations

from collections.abc import Iterator

import pytest

from tigrbl import TigrblApp, resolver as _resolver
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
def tail_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Stream(TableBase, GUIDPk):
        __tablename__ = "canonical_tail_streams"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (OpSpec(alias="tail", target="tail"),)

        name = Column(String, nullable=False)

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Stream)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, Stream, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_tail_op_projects_canonical_collection_route(tail_app_and_session) -> None:
    app, Stream, _ = tail_app_and_session

    routes = _route_map(app.core.Stream._model.rest.router)
    assert routes["tail"] == ("/stream", {"GET"})

    spec = next(item for item in OpSpec.collect(Stream) if item.alias == "tail")
    assert spec.target == "tail"
    assert spec.arity == "collection"


@pytest.mark.asyncio
async def test_tail_op_executes_realtime_handler_through_rpc(
    tail_app_and_session,
) -> None:
    app, _, db = tail_app_and_session

    result = await app.rpc.Stream.tail(
        {"stream": "orders", "limit": 7},
        db=db,
    )

    assert result["tailed"] is True
    assert result["stream"] == "orders"
    assert result["limit"] == 7
