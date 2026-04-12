from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

SessionFactory = sessionmaker


def _sqlite_url(mapping: Mapping[str, Any] | None, dsn: str | None) -> str:
    if dsn:
        return dsn
    config = dict(mapping or {})
    path = str(config.get("path") or "").strip()
    if not path:
        path = ":memory:"
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+pysqlite:///{path}"
    return "sqlite+pysqlite:///:memory:"


def sqlite_engine(
    *,
    mapping: Mapping[str, Any] | None = None,
    spec: Any | None = None,
    dsn: str | None = None,
    **_: Any,
) -> tuple[Any, SessionFactory]:
    config = dict(mapping or {})
    url = _sqlite_url(config, dsn)
    check_same_thread = bool(config.get("check_same_thread", False))

    eng = create_engine(
        url,
        connect_args={"check_same_thread": check_same_thread},
        future=True,
    )

    @event.listens_for(eng, "connect")
    def _configure_sqlite(dbapi_conn, conn_record):
        cur = dbapi_conn.cursor()
        try:
            cur.execute("PRAGMA foreign_keys=ON;")
        finally:
            cur.close()

    return eng, sessionmaker(bind=eng, expire_on_commit=False)


def sqlite_capabilities() -> dict[str, Any]:
    return {
        "transactional": True,
        "async_native": False,
        "isolation_levels": {"SERIALIZABLE", "READ UNCOMMITTED"},
        "read_only_enforced": False,
        "engine": "sqlite",
    }
