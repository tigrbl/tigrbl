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


def _finish_tx(db: Session) -> None:
    if db.in_transaction():
        db.commit()


@pytest.fixture()
def query_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Metric(TableBase, GUIDPk):
        __tablename__ = "canonical_query_metrics"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="count", target="count"),
            OpSpec(alias="exists", target="exists", arity="member"),
            OpSpec(alias="aggregate", target="aggregate"),
            OpSpec(alias="group_by", target="group_by"),
        )

        name = Column(String, nullable=False)

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Metric)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, Metric, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_query_ops_project_canonical_routes(query_app_and_session) -> None:
    app, Metric, _ = query_app_and_session

    routes = _route_map(app.core.Metric._model.rest.router)
    assert routes["count"] == ("/metric", {"GET"})
    assert routes["exists"] == ("/metric/{item_id}", {"GET"})
    assert routes["aggregate"] == ("/metric", {"POST"})
    assert routes["group_by"] == ("/metric", {"POST"})

    specs = {item.alias: item for item in OpSpec.collect(Metric)}
    assert specs["count"].target == "count"
    assert specs["count"].arity == "collection"
    assert specs["exists"].target == "exists"
    assert specs["exists"].arity == "member"
    assert specs["aggregate"].target == "aggregate"
    assert specs["aggregate"].arity == "collection"
    assert specs["group_by"].target == "group_by"
    assert specs["group_by"].arity == "collection"


@pytest.mark.asyncio
async def test_query_ops_execute_through_rpc(query_app_and_session) -> None:
    app, _, db = query_app_and_session

    first = await app.rpc.Metric.create({"name": "alpha"}, db=db)
    _finish_tx(db)
    await app.rpc.Metric.create({"name": "beta"}, db=db)
    _finish_tx(db)

    counted = await app.rpc.Metric.count({}, db=db)
    _finish_tx(db)
    exists = await app.rpc.Metric.exists({"id": first["id"]}, db=db)
    _finish_tx(db)
    missing = await app.rpc.Metric.exists(
        {"id": "00000000-0000-0000-0000-000000000000"},
        db=db,
    )
    _finish_tx(db)
    aggregated = await app.rpc.Metric.aggregate(
        {
            "rows": [{"value": 2}, {"value": 3}, {"value": 5}],
            "field": "value",
            "op": "sum",
        },
        db=db,
    )
    grouped = await app.rpc.Metric.group_by(
        {
            "rows": [
                {"kind": "a", "value": 2},
                {"kind": "a", "value": 3},
                {"kind": "b", "value": 5},
            ],
            "field": "kind",
            "value_field": "value",
            "agg": "sum",
        },
        db=db,
    )

    assert counted["count"] == 2
    assert exists["exists"] is True
    assert missing["exists"] is False
    assert aggregated == {"field": "value", "op": "sum", "value": 10.0, "count": 3}
    assert grouped == {
        "field": "kind",
        "agg": "sum",
        "groups": [
            {"key": "a", "value": 5.0, "rows": 2},
            {"key": "b", "value": 5.0, "rows": 1},
        ],
    }
