from __future__ import annotations

import pytest
from sqlalchemy import text

from tigrbl_base._base import EngineSessionBase
from tigrbl_engine_postgres.engine import postgres_engine
from tigrbl_engine_postgres.session import _PostgresAlchemySession, PostgresSession


def test_postgres_engine_uses_engine_session_class(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class DummyEngine:
        pass

    def fake_create_engine(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return DummyEngine()

    def fake_listens_for(*args, **kwargs):
        return lambda fn: fn

    monkeypatch.setattr("tigrbl_engine_postgres.engine.create_engine", fake_create_engine)
    monkeypatch.setattr("tigrbl_engine_postgres.engine.event.listens_for", fake_listens_for)

    _, maker = postgres_engine(dsn="postgresql+psycopg://user:pwd@localhost/db")
    session = maker()

    assert isinstance(session, PostgresSession)
    assert isinstance(session, EngineSessionBase)
    assert captured["args"] == ("postgresql+psycopg://user:pwd@localhost/db",)


@pytest.mark.asyncio
async def test_postgres_session_batch_methods_delegate_to_execute(monkeypatch) -> None:
    raw_session = _PostgresAlchemySession(bind=None)
    session = PostgresSession(raw_session)
    calls: list[tuple[object, object | None]] = []

    def fake_execute(stmt, params=None, *args, **kwargs):
        calls.append((stmt, params))
        return (stmt, params)

    monkeypatch.setattr(raw_session, "execute", fake_execute)

    insert_stmt = text("INSERT INTO items VALUES (:id)")
    many_result = await session.executemany(insert_stmt, [{"id": 1}])
    loop_result = await session.executeloop(
        [
            text("SELECT 1"),
            (text("SELECT :id"), {"id": 2}),
        ]
    )

    assert many_result == (insert_stmt, [{"id": 1}])
    assert loop_result[1][1] == {"id": 2}
    assert len(calls) == 3
