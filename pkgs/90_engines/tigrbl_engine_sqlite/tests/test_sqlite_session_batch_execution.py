from __future__ import annotations

from sqlalchemy import text

from tigrbl_engine_sqlite.engine import sqlite_engine
from tigrbl_engine_sqlite.session import SqliteSession


def test_sqlite_session_supports_executemany_and_executeloop() -> None:
    engine, maker = sqlite_engine()

    with maker() as session:
        assert isinstance(session, SqliteSession)

        session.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)"))
        session.executemany(
            text("INSERT INTO items (id, name) VALUES (:id, :name)"),
            [{"id": 1, "name": "alpha"}, {"id": 2, "name": "beta"}],
        )
        session.commit()

        results = session.executeloop(
            [
                text("SELECT name FROM items WHERE id = 1"),
                (text("SELECT name FROM items WHERE id = :id"), {"id": 2}),
            ]
        )

        assert [result.scalar_one() for result in results] == ["alpha", "beta"]

    engine.dispose()
