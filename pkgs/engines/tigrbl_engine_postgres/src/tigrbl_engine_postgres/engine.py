from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import quote_plus

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker


def _postgres_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    if dsn:
        return dsn
    if not mapping:
        raise ValueError("postgres requires either a DSN or a mapping")
    host = str(mapping.get("host") or "localhost")
    port = int(mapping.get("port") or 5432)
    user = quote_plus(str(mapping.get("user") or ""))
    pwd = quote_plus(str(mapping.get("pwd") or ""))
    db = quote_plus(str(mapping.get("db") or mapping.get("name") or ""))
    return f"postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}"


def postgres_engine(
    *,
    mapping: Mapping[str, Any] | None = None,
    spec: Any | None = None,
    dsn: str | None = None,
    **_: Any,
) -> tuple[Any, SessionFactory]:
    config = dict(mapping or {})
    url = _postgres_url(config, dsn)
    pool_size = int(config.get("pool_size") or getattr(spec, "pool_size", 10) or 10)
    max_overflow = int(config.get("max_overflow") or getattr(spec, "max", 20) or 20)

    eng = create_engine(
        url,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )

    @event.listens_for(eng, "connect")
    def _configure_postgres(dbapi_conn, conn_record):
        with dbapi_conn.cursor() as cur:
            cur.execute("SET statement_timeout = 0")
            cur.execute("SET lock_timeout = 0")

    return eng, sessionmaker(bind=eng, expire_on_commit=False)


def postgres_capabilities() -> dict[str, Any]:
    return {
        "transactional": True,
        "async_native": False,
        "isolation_levels": {
            "READ UNCOMMITTED",
            "READ COMMITTED",
            "REPEATABLE READ",
            "SERIALIZABLE",
        },
        "read_only_enforced": True,
        "engine": "postgres",
    }
