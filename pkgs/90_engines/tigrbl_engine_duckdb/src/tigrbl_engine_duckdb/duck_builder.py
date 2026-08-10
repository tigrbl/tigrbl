from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Tuple

import duckdb
from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from tigrbl_concrete._concrete._engine_session import wrap_sessionmaker

from tigrbl_core._spec.engine_session_spec import EngineSessionSpec

from .duck_session import DuckDBSession
from .sqlalchemy_adapter import DuckDBSqlAlchemyAdapter

SessionFactory = Callable[[], Any]
_NATIVE_MODES = {"native", "duckdb", "pure"}
_QUACK_PREFIX = "quack:"


def _config(
    mapping: Optional[Mapping[str, Any]],
    spec: Optional[Any],
    dsn: Optional[str],
) -> dict[str, Any]:
    config = dict(mapping or {})
    if dsn is not None:
        config.setdefault("dsn", dsn)
    for key in ("path", "read_only", "threads", "pragmas"):
        value = getattr(spec, key, None)
        if value is not None:
            config.setdefault(key, value)
    return config


def _duckdb_location(config: Mapping[str, Any]) -> str:
    location = (
        config.get("path")
        or config.get("database")
        or config.get("db")
        or config.get("dsn")
        or ":memory:"
    )
    return str(location)


def _is_quack_location(location: str) -> bool:
    return location.lower().startswith(_QUACK_PREFIX)


def _quoted_identifier(value: object) -> str:
    identifier = str(value or "").strip()
    if not identifier:
        raise ValueError("DuckDB Quack catalog must be a non-empty identifier")
    return f'"{identifier.replace(chr(34), chr(34) * 2)}"'


def _quoted_literal(value: object) -> str:
    return "'" + str(value).replace("'", "''") + "'"


def _configure_quack_connection(conn: Any, config: Mapping[str, Any]) -> None:
    """Attach a Quack server and make its catalog the connection default."""

    uri = _duckdb_location(config)
    if not _is_quack_location(uri):
        return

    catalog = _quoted_identifier(config.get("catalog") or "remote")
    options = ["TYPE QUACK"]
    token = config.get("token")
    if token is not None:
        options.append(f"TOKEN {_quoted_literal(token)}")
    if "disable_ssl" in config:
        options.append(
            f"DISABLE_SSL {'TRUE' if bool(config['disable_ssl']) else 'FALSE'}"
        )

    conn.execute(f"ATTACH {_quoted_literal(uri)} AS {catalog} ({', '.join(options)})")
    conn.execute(f"USE {catalog}")


def _mode(config: Mapping[str, Any]) -> str:
    return str(config.get("mode") or config.get("driver") or "sqlalchemy").lower()


def native_duckdb_engine(
    *,
    path: Optional[str] = None,
    read_only: bool = False,
    threads: Optional[int] = None,
    pragmas: Optional[Mapping[str, Any]] = None,
    mapping: Optional[Mapping[str, Any]] = None,
    spec: Optional[Any] = None,
    dsn: Optional[str] = None,
) -> Tuple[Any, SessionFactory]:
    """Build a pure DuckDB engine and a session factory yielding DuckDBSession."""

    config = _config(mapping, spec, dsn)
    if path is not None:
        config["path"] = path
    location = _duckdb_location(config)
    is_quack = _is_quack_location(location)
    db_path = ":memory:" if is_quack else location

    def mk_session(spec_in: Optional[EngineSessionSpec] = None) -> DuckDBSession:
        conn = duckdb.connect(db_path, read_only=read_only)
        if is_quack:
            _configure_quack_connection(conn, config)
        if threads is not None:
            conn.execute(f"PRAGMA threads={int(threads)}")
        if pragmas:
            for key, value in pragmas.items():
                if isinstance(value, bool):
                    value = "true" if value else "false"
                conn.execute(f"PRAGMA {key}={value}")
        return DuckDBSession(conn, spec_in)

    engine_handle = {"kind": "duckdb", "path": db_path, "read_only": read_only}
    if is_quack:
        engine_handle.update(
            {"dsn": location, "catalog": config.get("catalog") or "remote"}
        )
    return engine_handle, mk_session


def sqlalchemy_duckdb_engine(
    *,
    mapping: Optional[Mapping[str, Any]] = None,
    spec: Optional[Any] = None,
    dsn: Optional[str] = None,
    **_: Any,
) -> Tuple[Any, SessionFactory]:
    """Build a SQLAlchemy DuckDB engine for ORM DDL and canonical ops."""

    config = _config(mapping, spec, dsn)
    location = _duckdb_location(config)
    is_quack = _is_quack_location(location)
    db_path = ":memory:" if is_quack else location
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(
        URL.create("duckdb", database=db_path),
        future=True,
        poolclass=NullPool,
    )
    if is_quack:

        @event.listens_for(engine, "connect")
        def _attach_quack(dbapi_conn: Any, _: Any) -> None:
            _configure_quack_connection(dbapi_conn, config)

    maker = sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    def adapted_maker() -> DuckDBSqlAlchemyAdapter:
        return DuckDBSqlAlchemyAdapter(maker())

    return engine, wrap_sessionmaker(adapted_maker, EngineSessionSpec())


def duckdb_engine(
    *,
    path: Optional[str] = None,
    read_only: bool = False,
    threads: Optional[int] = None,
    pragmas: Optional[Mapping[str, Any]] = None,
    mapping: Optional[Mapping[str, Any]] = None,
    spec: Optional[Any] = None,
    dsn: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[Any, SessionFactory]:
    """Build DuckDB provider state.

    SQLAlchemy mode is the default because Tigrbl table apps need a SQLAlchemy
    bind for metadata.create_all(). Set mode="native" to retain the original
    pure duckdb session behavior.
    """

    config = _config(mapping, spec, dsn)
    if path is not None:
        config["path"] = path
    if read_only:
        config["read_only"] = read_only
    if threads is not None:
        config["threads"] = threads
    if pragmas is not None:
        config["pragmas"] = pragmas
    config.update({key: value for key, value in kwargs.items() if value is not None})

    if _mode(config) in _NATIVE_MODES:
        return native_duckdb_engine(
            path=_duckdb_location(config),
            read_only=bool(config.get("read_only", False)),
            threads=(
                int(config["threads"]) if config.get("threads") is not None else None
            ),
            pragmas=config.get("pragmas"),
            mapping=config,
            spec=spec,
            dsn=dsn,
        )
    return sqlalchemy_duckdb_engine(mapping=config, spec=spec, dsn=dsn)


def duckdb_capabilities(
    *,
    spec: Any | None = None,
    mapping: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Capability advertisement for session_ctx validation."""

    config = _config(mapping, spec, None)
    return {
        "transactional": True,
        "isolation_levels": {"snapshot", "repeatable_read"},
        "read_only_enforced": False,
        "async_native": False,
        "ddl": "native" if _mode(config) in _NATIVE_MODES else "sqlalchemy",
        "engine": "duckdb",
    }
