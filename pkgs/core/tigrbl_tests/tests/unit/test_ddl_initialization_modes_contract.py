from __future__ import annotations

import asyncio
import inspect

import pytest
from sqlalchemy import Column, Integer, text

from tigrbl import TableBase, TigrblApp, TigrblRouter, resolver
from tigrbl.factories.engine import mem, sqlitef
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column as TigrblColumn
from tigrbl.types import String


class DdlSyncWidget(TableBase, GUIDPk):
    __tablename__ = "ddl_sync_widgets_contract"

    name = TigrblColumn(String(100), nullable=False)


class DdlAsyncWidget(TableBase):
    __tablename__ = "ddl_async_widgets_contract"

    id = Column(Integer, primary_key=True)


class DdlMixedAsyncWidget(TableBase):
    __tablename__ = "ddl_mixed_async_widgets_contract"

    id = Column(Integer, primary_key=True)


class DdlMixedSyncWidget(TableBase):
    __tablename__ = "ddl_mixed_sync_widgets_contract"

    id = Column(Integer, primary_key=True)


def _run_if_awaitable(value: object) -> None:
    if inspect.isawaitable(value):
        asyncio.run(value)


@pytest.mark.unit
def test_sync_initialize_marks_ready_and_is_idempotent(tmp_path) -> None:
    app = TigrblApp(engine=sqlitef(str(tmp_path / "ddl-sync.sqlite"), async_=False))
    app.include_table(DdlSyncWidget)

    provider = resolver.resolve_provider(router=app, model=DdlSyncWidget)
    assert provider is not None
    resolver.require_schema_ready(provider)

    with pytest.raises(RuntimeError, match="Schema is not ready"):
        resolver.acquire(router=app, model=DdlSyncWidget, require_ready=True)

    _run_if_awaitable(app.initialize())
    _run_if_awaitable(app.initialize())

    db, release = resolver.acquire(router=app, model=DdlSyncWidget, require_ready=True)
    try:
        assert db.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        release()

    assert getattr(app, "_ddl_executed", False) is True


@pytest.mark.asyncio
async def test_async_initialize_returns_task_and_marks_ddl_executed() -> None:
    app = TigrblApp(engine=mem(async_=True))
    app.include_table(DdlAsyncWidget, prefix="")

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True


@pytest.mark.asyncio
async def test_mixed_sync_async_router_initialize_uses_async_task_mode() -> None:
    app = TigrblApp(engine=mem(async_=False))

    router = TigrblRouter(engine=mem(async_=True))
    router.include_table(DdlMixedAsyncWidget, prefix="")
    app.include_router(router)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(DdlMixedSyncWidget, prefix="")
    app.include_router(router)

    result = app.initialize()

    assert isinstance(result, asyncio.Task)

    await result

    assert getattr(app, "_ddl_executed", False) is True
    assert "DdlMixedAsyncWidget" in app.tables
    assert "DdlMixedSyncWidget" in app.tables
