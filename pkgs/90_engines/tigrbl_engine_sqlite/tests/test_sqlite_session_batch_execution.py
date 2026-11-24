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


@pytest.mark.asyncio
async def test_sqlite_explicit_and_implicit_provider_begin_identity() -> None:
    engine, maker = sqlite_engine()
    session = maker()
    try:
        await session.begin()
        assert session.transaction_id is None
        await session.execute(text("SELECT 1"))
        explicit = session.transaction_id
        assert explicit
        await session.execute(text("SELECT 2"))
        assert session.transaction_id == explicit
        await session.rollback()
        assert session.transaction_id is None
        await session.execute(text("SELECT 3"))
        implicit = session.transaction_id
        assert implicit and implicit != explicit
        await session.commit()
        assert session.transaction_id is None
        assert [(event["transaction_id"], event["outcome"]) for event in session.transaction_events()] == [
            (explicit, "begin"), (explicit, "rolled_back"),
            (implicit, "begin"), (implicit, "committed"),
        ]
        assert {event["engine_session_id"] for event in session.transaction_events()} == {session.engine_session_id}
    finally:
        await session.close()
        engine.dispose()


@pytest.mark.asyncio
async def test_sqlite_failed_commit_keeps_identity_until_confirmed_rollback() -> None:
    from sqlalchemy.exc import IntegrityError

    engine, maker = sqlite_engine()
    with engine.connect() as connection:
        connection.connection.driver_connection.execute("PRAGMA foreign_keys=ON")
    session = maker()
    try:
        await session.execute(text("CREATE TABLE parent (id INTEGER PRIMARY KEY)"))
        await session.execute(text(
            "CREATE TABLE child (parent_id INTEGER REFERENCES parent(id) DEFERRABLE INITIALLY DEFERRED)"
        ))
        await session.commit()

        await session.execute(text("INSERT INTO child VALUES (42)"))
        transaction_id = session.transaction_id
        assert transaction_id
        with pytest.raises(IntegrityError):
            await session.commit()
        assert session.transaction_id == transaction_id
        await session.rollback()
        assert session.transaction_id is None
        assert [event["outcome"] for event in session.transaction_events()
                if event["transaction_id"] == transaction_id] == ["begin", "rolled_back"]
    finally:
        await session.close()
        engine.dispose()
