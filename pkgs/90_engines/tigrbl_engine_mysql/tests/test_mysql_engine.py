import asyncio

from sqlalchemy import text
from tigrbl_base._base import EngineSessionBase
from tigrbl_engine_mysql.engine import _mysql_url, mysql_engine
from tigrbl_engine_mysql.session import MySQLSession, _MySQLAlchemySession


def test_mapping_builds_escaped_utf8mb4_dsn() -> None:
    url = _mysql_url({"user": "port wyrm", "password": "p@ss", "host": "db", "name": "control"}, None)
    assert url == "mysql+pymysql://port+wyrm:p%40ss@db:3306/control?charset=utf8mb4"


def test_engine_factory_returns_tigrbl_engine_session(monkeypatch) -> None:
    captured = {}

    class DummyEngine:
        pass

    def fake_create_engine(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return DummyEngine()
    monkeypatch.setattr("tigrbl_engine_mysql.engine.create_engine", fake_create_engine)
    _, maker = mysql_engine(dsn="mysql+pymysql://user:pwd@localhost/db")
    session = maker()
    assert isinstance(session, MySQLSession)
    assert isinstance(session, EngineSessionBase)
    assert captured["kwargs"]["pool_pre_ping"] is True


def test_batch_methods_delegate_to_engine_session() -> None:
    raw = _MySQLAlchemySession(bind=None)
    session = MySQLSession(raw)
    calls = []
    raw.execute = lambda stmt, params=None, *args, **kwargs: calls.append((stmt, params)) or params
    async def exercise() -> None:
        await session.executemany(text("INSERT INTO x VALUES (:id)"), [{"id": 1}])
        await session.executeloop([text("SELECT 1"), (text("SELECT :id"), {"id": 2})])

    asyncio.run(exercise())
    assert len(calls) == 3
