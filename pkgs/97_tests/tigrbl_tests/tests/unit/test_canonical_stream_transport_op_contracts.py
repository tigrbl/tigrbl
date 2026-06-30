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
def stream_transport_app_and_session() -> Iterator[tuple[TigrblApp, type, Session]]:
    class Stream(TableBase, GUIDPk):
        __tablename__ = "canonical_stream_transport_streams"
        __allow_unmapped__ = True
        __tigrbl_ops__ = (
            OpSpec(alias="append_chunk", target="append_chunk"),
            OpSpec(alias="send_datagram", target="send_datagram"),
        )

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


def test_stream_transport_ops_project_canonical_routes(
    stream_transport_app_and_session,
) -> None:
    app, Stream, _ = stream_transport_app_and_session

    routes = _route_map(app.core.Stream._model.rest.router)
    assert routes["append_chunk"] == ("/stream", {"POST"})
    assert routes["send_datagram"] == ("/stream", {"POST"})

    specs = {item.alias: item for item in OpSpec.collect(Stream)}
    assert specs["append_chunk"].target == "append_chunk"
    assert specs["append_chunk"].arity == "collection"
    assert specs["send_datagram"].target == "send_datagram"
    assert specs["send_datagram"].arity == "collection"


@pytest.mark.asyncio
async def test_stream_transport_ops_execute_realtime_handlers_through_rpc(
    stream_transport_app_and_session,
) -> None:
    app, _, db = stream_transport_app_and_session

    appended = await app.rpc.Stream.append_chunk(
        {"stream": "orders", "chunk": "abcdef"},
        db=db,
    )
    sent = await app.rpc.Stream.send_datagram(
        {"route": "edge-a", "ttl": 30},
        db=db,
    )

    assert appended["appended"] is True
    assert appended["stream"] == "orders"
    assert appended["size"] == 6
    assert sent["sent"] is True
    assert sent["route"] == "edge-a"
    assert sent["ttl"] == 30
