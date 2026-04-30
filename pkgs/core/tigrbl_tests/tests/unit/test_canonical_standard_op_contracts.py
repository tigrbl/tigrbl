from __future__ import annotations

from collections.abc import Iterator

import pytest

from tigrbl import TigrblApp, resolver as _resolver
from tigrbl._spec import OpSpec
from tigrbl.factories.column import acol as spec_acol
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk, Mergeable, Replaceable
from tigrbl.orm.tables import TableBase
from tigrbl.types import F, IO, S, Session, String, uuid4


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
def app_and_session() -> Iterator[tuple[TigrblApp, Session]]:
    class Widget(TableBase, GUIDPk, Replaceable, Mergeable):
        __tablename__ = "canonical_standard_op_widgets"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="merge", target="merge"),
            OpSpec(alias="checkpoint", target="checkpoint"),
        )

        name = spec_acol(
            storage=S(type_=String(50), nullable=False),
            field=F(py_type=str),
            io=IO(
                in_verbs=("create", "update", "replace", "merge"),
                out_verbs=("read", "list", "merge"),
                mutable_verbs=("create", "update", "replace", "merge"),
            ),
        )

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Widget, mount_router=False)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_standard_canonical_ops_project_rest_routes(app_and_session) -> None:
    app, _ = app_and_session
    routes = _route_map(app.core.Widget._model.rest.router)

    assert routes["create"] == ("/widget", {"POST"})
    assert routes["read"] == ("/widget/{item_id}", {"GET"})
    assert routes["update"] == ("/widget/{item_id}", {"PATCH"})
    assert routes["replace"] == ("/widget/{item_id}", {"PUT"})
    assert routes["merge"] == ("/widget/{item_id}", {"PATCH"})
    assert routes["delete"] == ("/widget/{item_id}", {"DELETE"})
    assert routes["list"] == ("/widget", {"GET"})
    assert routes["clear"] == ("/widget", {"DELETE"})
    assert routes["checkpoint"] == ("/widget", {"POST"})


@pytest.mark.asyncio
async def test_standard_canonical_ops_execute_through_rpc(app_and_session) -> None:
    app, db = app_and_session

    created = await app.rpc.Widget.create({"name": "alpha"}, db=db)
    _finish_tx(db)
    read = await app.rpc.Widget.read({"id": created["id"]}, db=db)
    _finish_tx(db)
    updated = await app.rpc.Widget.update(
        {"name": "beta"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    _finish_tx(db)
    replaced = await app.rpc.Widget.replace(
        {"name": "gamma"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    _finish_tx(db)
    merged = await app.rpc.Widget.merge(
        {"id": created["id"], "name": "delta"},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    _finish_tx(db)
    listed = await app.rpc.Widget.list({}, db=db)
    _finish_tx(db)
    checkpointed = await app.rpc.Widget.checkpoint({"cursor": "c1"}, db=db)
    _finish_tx(db)
    deleted = await app.rpc.Widget.delete(
        {},
        db=db,
        ctx={"path_params": {"id": created["id"]}},
    )
    _finish_tx(db)
    cleared = await app.rpc.Widget.clear({"filters": {}}, db=db)
    _finish_tx(db)

    assert read["id"] == created["id"]
    assert updated["name"] == "beta"
    assert replaced["name"] == "gamma"
    assert merged["name"] == "delta"
    assert any(row["id"] == created["id"] for row in listed)
    assert checkpointed == {"checkpointed": True, "cursor": "c1"}
    assert deleted == {"deleted": 1}
    assert cleared == {"deleted": 0}


def test_checkpoint_is_canonical_collection_op() -> None:
    class Widget(TableBase, GUIDPk):
        __tablename__ = "canonical_checkpoint_projection"
        __tigrbl_ops__ = (OpSpec(alias="checkpoint", target="checkpoint"),)

    spec = next(item for item in OpSpec.collect(Widget) if item.alias == "checkpoint")

    assert spec.target == "checkpoint"
    assert spec.arity == "collection"
