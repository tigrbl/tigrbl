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
def pubsub_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Topic(TableBase, GUIDPk):
        __tablename__ = "canonical_pubsub_topics"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="publish", target="publish"),
            OpSpec(alias="subscribe", target="subscribe"),
        )

        name = Column(String, nullable=False)

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Topic)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, Topic, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_pubsub_ops_project_canonical_collection_routes(
    pubsub_app_and_session,
) -> None:
    app, Topic, _ = pubsub_app_and_session

    routes = _route_map(app.core.Topic._model.rest.router)
    assert routes["publish"] == ("/topic", {"POST"})
    assert routes["subscribe"] == ("/topic", {"GET"})

    specs = {item.alias: item for item in OpSpec.collect(Topic)}
    assert specs["publish"].target == "publish"
    assert specs["publish"].arity == "collection"
    assert specs["subscribe"].target == "subscribe"
    assert specs["subscribe"].arity == "collection"


@pytest.mark.asyncio
async def test_pubsub_ops_execute_realtime_handlers_through_rpc(
    pubsub_app_and_session,
) -> None:
    app, _, db = pubsub_app_and_session

    published = await app.rpc.Topic.publish(
        {"channel": "orders", "event": {"id": "evt-1"}},
        db=db,
    )
    subscribed = await app.rpc.Topic.subscribe(
        {"channel": "orders", "cursor": "c-10"},
        db=db,
    )

    assert published["published"] is True
    assert published["channel"] == "orders"
    assert published["event"] == {"id": "evt-1"}
    assert subscribed["subscribed"] is True
    assert subscribed["channel"] == "orders"
    assert subscribed["cursor"] == "c-10"
