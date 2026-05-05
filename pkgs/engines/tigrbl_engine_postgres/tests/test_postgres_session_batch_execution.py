from __future__ import annotations

from sqlalchemy import text

from tigrbl_engine_postgres.engine import postgres_engine
from tigrbl_engine_postgres.session import PostgresSession


def test_postgres_engine_uses_batch_session_class(monkeypatch) -> None:
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

    assert issubclass(maker.class_, PostgresSession)
    assert captured["args"] == ("postgresql+psycopg://user:pwd@localhost/db",)


def test_postgres_session_batch_methods_delegate_to_execute(monkeypatch) -> None:
    session = PostgresSession(bind=None)
    calls: list[tuple[object, object | None]] = []

    def fake_execute(stmt, params=None, *args, **kwargs):
        calls.append((stmt, params))
        return (stmt, params)

    monkeypatch.setattr(session, "execute", fake_execute)

    insert_stmt = text("INSERT INTO items VALUES (:id)")
    many_result = session.executemany(insert_stmt, [{"id": 1}])
    loop_result = session.executeloop(
        [
            text("SELECT 1"),
            (text("SELECT :id"), {"id": 2}),
        ]
    )

    assert many_result == (insert_stmt, [{"id": 1}])
    assert loop_result[1][1] == {"id": 2}
    assert len(calls) == 3
