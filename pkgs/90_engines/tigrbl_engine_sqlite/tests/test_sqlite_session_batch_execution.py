from __future__ import annotations

import pytest
from sqlalchemy import text

from tigrbl_base._base import EngineSessionBase
from tigrbl_engine_sqlite.engine import sqlite_engine
from tigrbl_engine_sqlite.session import SqliteSession


@pytest.mark.asyncio
async def test_sqlite_session_supports_executemany_and_executeloop() -> None:
    engine, maker = sqlite_engine()

    session = maker()
    try:
        assert isinstance(session, SqliteSession)
        assert isinstance(session, EngineSessionBase)

        await session.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"))
        await session.executemany(
            text("INSERT INTO items (id, name) VALUES (:id, :name)"),
            [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}],
        )
        await session.commit()

        results = await session.executeloop(
            [
                text("SELECT name FROM items WHERE id = 1"),
                (text("SELECT name FROM items WHERE id = :id"), {"id": 2}),
            ]
        )

        assert [result.scalar_one() for result in results] == ["alpha", "beta"]
    finally:
        await session.close()

    engine.dispose()
