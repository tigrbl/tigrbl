from __future__ import annotations

import pytest
from sqlalchemy.orm.exc import NoResultFound

from tigrbl import Column, Schema, TableBase, build_schemas
from tigrbl.specs import F, IO, S
from tigrbl.types import JSON, Float, String
from tigrbl_core._spec import OpSpec
from tigrbl_ops_oltp import clear, count, create, delete, exists, list, read

from tigrbl_engine_memlru.lru import LRUCache
from tigrbl_engine_memlru.session import LRUSession


class CacheEntry(TableBase):
    __tablename__ = "memlru_canonical_entries"

    key = Column(
        storage=S(String, primary_key=True, nullable=False, autoincrement=False),
        field=F(py_type=str),
        io=IO(
            in_verbs=("create", "read", "delete"),
            out_verbs=("create", "read", "list"),
        ),
    )
    value = Column(
        storage=S(JSON, nullable=False),
        field=F(py_type=object),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )
    cost = Column(
        storage=S(Float, nullable=True),
        field=F(py_type=float),
        io=IO(in_verbs=("create",), out_verbs=("create", "read", "list")),
    )


def test_public_schema_materializer_honors_column_io_directions() -> None:
    specs = tuple(
        OpSpec(alias=target, target=target)
        for target in ("create", "read", "delete", "clear")
    )

    build_schemas(CacheEntry, specs)
    schemas = Schema.collect(CacheEntry)

    assert set(schemas["create"]["in"].model_fields) == {"key", "value", "cost"}
    assert set(schemas["create"]["out"].model_fields) == {"key", "value", "cost"}
    assert set(schemas["read"]["in"].model_fields) == {"key"}
    assert set(schemas["read"]["out"].model_fields) == {"key", "value", "cost"}
    assert set(schemas["delete"]["in"].model_fields) == {"key"}
    assert set(schemas["delete"]["out"].model_fields) == {"deleted"}
    assert schemas["clear"]["in"].model_fields == {}
    assert set(schemas["clear"]["out"].model_fields) == {"deleted"}


@pytest.mark.asyncio
async def test_memlru_executes_canonical_record_operations() -> None:
    session = LRUSession(LRUCache(max_items=2))

    created = await create(
        CacheEntry,
        {"key": "alpha", "value": {"score": 1}, "cost": 2.0},
        session,
    )
    assert created.key == "alpha"
    assert created.value == {"score": 1}

    fetched = await read(CacheEntry, "alpha", session)
    assert fetched.key == "alpha"
    assert fetched.cost == 2.0
    assert (await exists(CacheEntry, "alpha", session)) == {"exists": True}
    assert (await count(model=CacheEntry, db=session)) == {"count": 1}
    assert [row.key for row in await list(model=CacheEntry, db=session)] == [
        "alpha"
    ]

    assert await delete(CacheEntry, "alpha", session) == {"deleted": 1}
    with pytest.raises(NoResultFound):
        await read(CacheEntry, "alpha", session)


@pytest.mark.asyncio
async def test_memlru_clear_and_engine_session_contract() -> None:
    session = LRUSession(LRUCache(max_items=3))
    for key in ("alpha", "beta"):
        await create(CacheEntry, {"key": key, "value": key}, session)

    assert (await session.get(CacheEntry, "alpha")).value == "alpha"
    assert await clear(model=CacheEntry, db=session) == {"deleted": 2}
    assert await session.get(CacheEntry, "alpha") is None

    await session.close()
    with pytest.raises(RuntimeError, match="session is closed"):
        session.stats()
