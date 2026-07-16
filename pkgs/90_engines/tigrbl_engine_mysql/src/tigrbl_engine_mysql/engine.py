from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .session import MySQLSession, _MySQLAlchemySession

SessionFactory = Callable[[], MySQLSession]


def _mysql_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    if dsn:
        return dsn
    if not mapping:
        raise ValueError("mysql requires either a DSN or a mapping")
    user = quote_plus(str(mapping.get("user") or ""))
    password = quote_plus(str(mapping.get("pwd") or mapping.get("password") or ""))
    host = str(mapping.get("host") or "localhost")
    port = int(mapping.get("port") or 3306)
    database = quote_plus(str(mapping.get("db") or mapping.get("name") or mapping.get("database") or ""))
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"


def mysql_engine(*, mapping: Mapping[str, Any] | None = None, spec: Any | None = None,
                 dsn: str | None = None, **_: Any) -> tuple[Any, SessionFactory]:
    config = dict(mapping or {})
    eng = create_engine(
        _mysql_url(config, dsn),
        pool_size=int(config.get("pool_size") or getattr(spec, "pool_size", 10) or 10),
        max_overflow=int(config.get("max_overflow") or getattr(spec, "max", 20) or 20),
        pool_pre_ping=bool(config.get("pool_pre_ping", True)),
        future=True,
    )
    raw_maker = sessionmaker(bind=eng, class_=_MySQLAlchemySession, expire_on_commit=False)

    def make_session() -> MySQLSession:
        return MySQLSession(raw_maker(), EngineSessionSpec())

    return eng, make_session


def mysql_capabilities() -> dict[str, Any]:
    return {
        "transactional": True,
        "async_native": False,
        "isolation_levels": {"READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"},
        "read_only_enforced": True,
        "engine": "mysql",
    }

