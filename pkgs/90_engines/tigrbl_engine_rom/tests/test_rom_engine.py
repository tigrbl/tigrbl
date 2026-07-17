from __future__ import annotations

from dataclasses import dataclass

import pytest
from sqlalchemy import Integer, String, delete, or_, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from tigrbl.factories.table import defineTableSpec
from tigrbl_base._base import EngineBase
from tigrbl_concrete._concrete import engine_resolver
from tigrbl_core._spec.engine_spec import EngineSpec
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec
from tigrbl_ops_oltp.crud.ops import merge, replace as replace_row, update

from tigrbl_engine_rom import (
    ROMEngine,
    ROMSession,
    build_rom,
    capabilities,
    register,
)


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    rank: Mapped[int] = mapped_column(Integer)


@dataclass
class Record:
    id: int
    value: str


def test_engine_detaches_and_protects_nested_source_data() -> None:
    source = [{"id": 1, "value": "alpha", "tags": ["stable"]}]
    engine = ROMEngine(source)
    assert isinstance(engine, EngineBase)
    assert engine.to_provider() is engine

    source[0]["value"] = "changed"
    source[0]["tags"].append("mutated")
    first = engine.get(1)
    assert first == {"id": 1, "value": "alpha", "tags": ["stable"]}

    assert first is not None
    first["value"] = "caller mutation"
    first["tags"].append("caller mutation")
    assert engine.get(1) == {
        "id": 1,
        "value": "alpha",
        "tags": ["stable"],
    }


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([{"value": "missing"}], "missing primary key"),
        ([{"id": 1}, {"id": 1}], "duplicate primary key"),
        (["not-a-row"], "must be a mapping"),
    ],
)
def test_engine_rejects_invalid_rom_images(rows, message: str) -> None:
    with pytest.raises((TypeError, ValueError), match=message):
        ROMEngine(rows)


def test_engine_supports_a_custom_primary_key() -> None:
    engine = ROMEngine(
        [{"name": "theme", "value": "dark"}],
        primary_key="name",
    )
    assert engine.primary_key == "name"
    assert engine.get("theme") == {"name": "theme", "value": "dark"}


def test_rom_configuration_is_an_input_to_a_table_spec() -> None:
    rom = {
        "kind": "rom",
        "rows": [{"id": 1, "name": "one", "rank": 1}],
        "primary_key": "id",
    }
    Spec = defineTableSpec(engine=rom)

    assert Spec.table_config["engine"] is rom
    assert Spec.table_config["db"] is rom


@pytest.mark.asyncio
async def test_table_bound_engine_resolves_a_rom_session_for_that_model() -> None:
    register()
    engine_resolver.reset(dispose=False)
    rom = {
        "kind": "rom",
        "rows": [{"id": 1, "name": "one", "rank": 1}],
    }
    Spec = defineTableSpec(engine=rom)
    engine_resolver.register_table(Widget, Spec.table_config["engine"])

    session, _release = engine_resolver.acquire(model=Widget)
    try:
        widget = await session.get(Widget, 1)
        assert widget.name == "one"
    finally:
        await session.close()
        engine_resolver.reset(dispose=False)


@pytest.mark.asyncio
async def test_session_supports_point_reads_scans_and_sqlalchemy_selects() -> None:
    engine = ROMEngine(
        [
            {"id": 1, "name": "one", "rank": 2},
            {"id": 2, "name": "two", "rank": 1},
            {"id": 3, "name": "three", "rank": 3},
        ]
    )
    session = ROMSession(engine)

    widget = await session.get(Widget, 2)
    assert (widget.id, widget.name, widget.rank) == (2, "two", 1)
    assert await session.get(Widget, 99) is None
    assert session.query_rows(lambda row: row["rank"] > 1) == [
        {"id": 1, "name": "one", "rank": 2},
        {"id": 3, "name": "three", "rank": 3},
    ]

    result = await session.execute(
        select(Widget)
        .where(Widget.id.in_([1, 3]))
        .order_by(Widget.rank.desc())
        .limit(1)
    )
    assert [item.id for item in result.scalars().all()] == [3]

    result = await session.execute(select(Widget).where(Widget.name == "two"))
    assert result.scalar_one().id == 2

    with pytest.raises(NotImplementedError, match="conjunctions"):
        await session.execute(select(Widget).where(or_(Widget.id == 1, Widget.id == 2)))


@pytest.mark.asyncio
async def test_session_is_always_read_only_and_lifecycle_safe() -> None:
    engine = ROMEngine([{"id": 1, "value": "alpha"}])
    session = ROMSession(engine, EngineSessionSpec(read_only=False))
    assert session.read_only is True

    with pytest.raises(RuntimeError, match="read-only"):
        session.add(Record(2, "beta"))
    with pytest.raises(RuntimeError, match="read-only"):
        await session.delete(Record(1, "alpha"))
    with pytest.raises(RuntimeError, match="read-only"):
        await session.execute(delete(Widget))
    with pytest.raises(RuntimeError, match="read-only"):
        await session.executemany(select(Widget), [{"id": 1}])

    await session.begin()
    assert session.in_transaction() is True
    await session.commit()
    assert session.in_transaction() is False
    await session.close()
    assert session.in_transaction() is False
    with pytest.raises(RuntimeError, match="closed"):
        session.get_row(1)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", [update, replace_row, merge])
async def test_generic_mutation_helpers_fail_closed(operation) -> None:
    engine = ROMEngine([{"id": 1, "name": "original", "rank": 1}])
    session = ROMSession(engine)

    with pytest.raises(RuntimeError, match="read-only"):
        await operation(Widget, 1, {"name": operation.__name__}, session)
    assert engine.get(1)["name"] == "original"


@pytest.mark.asyncio
async def test_rollback_restores_locally_mutated_read_objects() -> None:
    session = ROMSession(ROMEngine([{"id": 1, "name": "original", "rank": 1}]))
    widget = await session.get(Widget, 1)
    widget.name = "local mutation"

    with pytest.raises(RuntimeError, match="read-only"):
        await session.commit()
    await session.rollback()
    assert widget.name == "original"


def test_plugin_factory_and_capabilities_describe_rom_semantics() -> None:
    engine, maker = build_rom(mapping={"rows": [{"id": 1, "value": "alpha"}]})
    assert isinstance(engine, ROMEngine)
    assert isinstance(maker(), ROMSession)
    assert capabilities()["read_only_enforced"] is True
    assert capabilities()["storage"] == "immutable-memory"
    assert capabilities()["binding_scopes"] == {"table"}
    with pytest.raises(ValueError, match="not a DSN"):
        build_rom(dsn="rom://image")


def test_registration_builds_through_engine_spec() -> None:
    register()
    spec = EngineSpec.from_any({"kind": "rom", "rows": [{"id": 1, "value": "alpha"}]})
    assert spec is not None
    engine, maker = spec.build()
    assert isinstance(engine, EngineBase)
    assert engine.spec is spec
    assert engine.get(1) == {"id": 1, "value": "alpha"}
    assert isinstance(maker(), ROMSession)
    assert spec.supports()["read_only_enforced"] is True


@pytest.mark.asyncio
async def test_engine_base_batch_surface_delegates_to_rom_sessions() -> None:
    engine = ROMEngine([{"id": 1, "name": "one", "rank": 1}])

    results = await engine.executeloop([select(Widget)])
    assert results[0].scalar_one().name == "one"
    with pytest.raises(RuntimeError, match="read-only"):
        await engine.executemany(select(Widget), [{"id": 1}])
