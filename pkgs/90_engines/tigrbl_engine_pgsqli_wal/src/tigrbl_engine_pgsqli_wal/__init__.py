"""PostgreSQL/SQLite WAL engines for Tigrbl.

Exports:
- build_postgres_wal_engine, postgres_wal_capabilities
- build_sqlite_wal_engine, sqlite_wal_capabilities
- PostgresWALSession, SqliteWALSession
- register() : entry-point hook (group 'tigrbl.engine')
"""

from __future__ import annotations

from .engines.postgres_wal_engine import (
    build_postgres_wal_engine,
    postgres_wal_capabilities,
)
from .engines.sqlite_wal_engine import build_sqlite_wal_engine, sqlite_wal_capabilities
from .sessions.postgres_wal_session import PostgresWALSession
from .sessions.sqlite_wal_session import SqliteWALSession


class _Registration:
    def __init__(self, builder, capability_provider):
        self._builder = builder
        self._capability_provider = capability_provider

    def build(self, *, mapping, spec, dsn):
        return self._builder(mapping=mapping, spec=spec, dsn=dsn)

    def capabilities(self, *, spec, mapping=None):
        return self._capability_provider()


def register() -> None:
    # Late import to avoid importing tigrbl at module import-time
    from tigrbl.engine.registry import register_engine

    register_engine(
        "postgres_wal",
        _Registration(build_postgres_wal_engine, postgres_wal_capabilities),
    )
    register_engine(
        "sqlite_wal",
        _Registration(build_sqlite_wal_engine, sqlite_wal_capabilities),
    )


__all__ = [
    "build_postgres_wal_engine",
    "postgres_wal_capabilities",
    "build_sqlite_wal_engine",
    "sqlite_wal_capabilities",
    "PostgresWALSession",
    "SqliteWALSession",
    "register",
]
