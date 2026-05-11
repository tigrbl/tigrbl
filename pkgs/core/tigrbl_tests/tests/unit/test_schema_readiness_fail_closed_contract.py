import pytest
from sqlalchemy import text

from tigrbl import TableBase, TigrblApp, resolver
from tigrbl._spec import EngineSpec
from tigrbl.factories.engine import sqlitef
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


class ReadinessRecord(TableBase, GUIDPk):
    __tablename__ = "readiness_records"
    name = Column(String(100), nullable=False)


def test_schema_readiness_guard_blocks_request_session_before_ready() -> None:
    provider = resolver.register_engine(
        "guarded",
        EngineSpec(kind="sqlite", memory=True, name="guarded"),
    )
    resolver.set_default_engine_name("guarded")
    resolver.require_schema_ready(provider)

    with pytest.raises(RuntimeError, match="Schema is not ready"):
        resolver.acquire(engine_name="guarded", require_ready=True)

    db, release = resolver.acquire(engine_name="guarded", require_ready=False)
    try:
        assert db.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        release()


def test_initialize_marks_resolved_provider_schema_ready(tmp_path) -> None:
    app = TigrblApp(engine=sqlitef(str(tmp_path / "readiness.sqlite")))
    app.include_table(ReadinessRecord)

    provider = resolver.resolve_provider(router=app, model=ReadinessRecord)
    assert provider is not None
    resolver.require_schema_ready(provider)

    with pytest.raises(RuntimeError, match="Schema is not ready"):
        resolver.acquire(router=app, model=ReadinessRecord, require_ready=True)

    app.initialize()

    db, release = resolver.acquire(router=app, require_ready=True)
    try:
        assert db.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        release()
