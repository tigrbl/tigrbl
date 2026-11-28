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
def file_transfer_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Blob(TableBase, GUIDPk):
        __tablename__ = "canonical_file_transfer_blobs"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="upload", target="upload"),
            OpSpec(alias="download", target="download"),
        )

        name = Column(String, nullable=False)

    cfg = mem(async_=False)
    app = TigrblApp(engine=cfg)
    app.include_table(Blob)
    app.initialize()

    prov = _resolver.resolve_provider()
    engine, maker = prov.ensure()
    session: Session = maker()
    try:
        yield app, Blob, session
    finally:
        session.close()
        engine.dispose()
        _resolver.set_default(None)


def test_file_transfer_ops_project_canonical_collection_routes(
    file_transfer_app_and_session,
) -> None:
    app, Blob, _ = file_transfer_app_and_session

    routes = _route_map(app.core.Blob._model.rest.router)
    assert routes["upload"] == ("/blob", {"POST"})
    assert routes["download"] == ("/blob", {"GET"})

    specs = {item.alias: item for item in OpSpec.collect(Blob)}
    assert specs["upload"].target == "upload"
    assert specs["upload"].arity == "collection"
    assert specs["download"].target == "download"
    assert specs["download"].arity == "collection"


@pytest.mark.asyncio
async def test_file_transfer_ops_execute_realtime_handlers_through_rpc(
    file_transfer_app_and_session,
) -> None:
    app, _, db = file_transfer_app_and_session

    uploaded = await app.rpc.Blob.upload(
        {"name": "report.bin", "content": b"abcdef"},
        db=db,
    )
    downloaded = await app.rpc.Blob.download(
        {"name": "report.bin", "checkpoint": "ck-7"},
        db=db,
    )

    assert uploaded["uploaded"] is True
    assert uploaded["name"] == "report.bin"
    assert uploaded["size"] == 6
    assert downloaded["downloaded"] is True
    assert downloaded["name"] == "report.bin"
    assert downloaded["checkpoint"] == "ck-7"
