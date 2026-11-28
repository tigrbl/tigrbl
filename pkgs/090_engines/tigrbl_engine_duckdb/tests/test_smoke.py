from __future__ import annotations

import inspect
from pathlib import Path

import pytest
from sqlalchemy import text

from tigrbl import TableBase, TigrblApp
from tigrbl.types import Column, String
from tigrbl_core._spec import plugins, registry
from tigrbl_core._spec import AppSpec, EngineSpec
from tigrbl_concrete._concrete import engine_resolver as resolver
from tigrbl_concrete._concrete._engine_session import EngineSession
from tigrbl_engine_duckdb import (
    DuckDBSession,
    duckdb_engine,
)
from tigrbl_engine_duckdb.duck_builder import _configure_quack_connection
from tigrbl_engine_duckdb.plugin import register


class DuckDbDdlWidget(TableBase):
    __tablename__ = "duckdb_engine_ddl_widgets"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


class DuckDbNativeWidget(TableBase):
    __tablename__ = "duckdb_engine_native_widgets"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


def _run_if_awaitable(value: object) -> None:
    if inspect.isawaitable(value):
        import asyncio

        asyncio.run(value)


@pytest.fixture(autouse=True)
def _reset_resolver() -> None:
    resolver.reset()
    register()
    yield
    resolver.reset()


def test_package_assets_present() -> None:
    package_dir = Path(__file__).resolve().parents[1]
    assert (package_dir / "README.md").is_file()
    assert (package_dir / "LICENSE").is_file()
    assert (package_dir / "pyproject.toml").is_file()


def test_engine_plugin_loader_discovers_duckdb_entry_point() -> None:
    registry._ENGINE_REGISTRY.pop("duckdb", None)
    plugins._LOADED = False

    plugins.load_engine_plugins()

    assert registry.get_engine_registration("duckdb") is not None


@pytest.mark.asyncio
async def test_duckdb_locations_resolve_to_file_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    location = "nested/direct.duckdb"
    spec = EngineSpec.from_any(location)

    assert spec is not None
    assert spec.kind == "duckdb"
    engine, maker = spec.build()
    try:
        session = maker()
        await session.execute(text("SELECT 1"))
        await session.close()
        assert Path(engine.url.database) == Path(location)
        assert (tmp_path / location).is_file()
    finally:
        engine.dispose()


def test_quack_location_attaches_remote_catalog_without_creating_local_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RecordingConnection:
        def __init__(self) -> None:
            self.calls: list[tuple[str, list[object] | None]] = []

        def execute(
            self, statement: str, parameters: list[object] | None = None
        ) -> None:
            self.calls.append((statement, parameters))

    monkeypatch.chdir(tmp_path)
    connection = RecordingConnection()
    config = {
        "dsn": "quack://group'sum-duckdb:9494",
        "catalog": 'group"sum',
        "token": "secret'-token",
        "disable_ssl": True,
    }

    _configure_quack_connection(connection, config)

    assert connection.calls == [
        (
            "ATTACH 'quack://group''sum-duckdb:9494' AS \"group\"\"sum\" "
            "(TYPE QUACK, TOKEN 'secret''-token', DISABLE_SSL TRUE)",
            None,
        ),
        ('USE "group""sum"', None),
    ]
    assert not (tmp_path / "group'sum-duckdb:9494").exists()


def test_sqlalchemy_quack_engine_uses_in_memory_client_and_connect_hook(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    callbacks: list[object] = []

    def capture_listener(engine: object, event_name: str):
        assert event_name == "connect"

        def decorate(callback: object) -> object:
            callbacks.append(callback)
            return callback

        return decorate

    monkeypatch.setattr(
        "tigrbl_engine_duckdb.duck_builder.event.listens_for",
        capture_listener,
    )
    engine, _ = duckdb_engine(dsn="quack://groupsum-duckdb:9494")
    try:
        assert engine.url.database == ":memory:"
        assert len(callbacks) == 1
    finally:
        engine.dispose()


def test_native_quack_engine_uses_in_memory_client_and_attaches_remote(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RecordingConnection:
        def __init__(self) -> None:
            self.calls: list[tuple[str, list[object] | None]] = []

        def execute(
            self, statement: str, parameters: list[object] | None = None
        ) -> None:
            self.calls.append((statement, parameters))

    connection = RecordingConnection()
    connect_calls: list[tuple[str, bool]] = []

    def connect(path: str, *, read_only: bool) -> RecordingConnection:
        connect_calls.append((path, read_only))
        return connection

    monkeypatch.setattr("tigrbl_engine_duckdb.duck_builder.duckdb.connect", connect)
    engine, maker = duckdb_engine(
        mapping={
            "kind": "duckdb",
            "dsn": "quack://groupsum-duckdb:9494",
            "token": "secret-token",
            "mode": "native",
        }
    )

    session = maker()

    assert isinstance(session, DuckDBSession)
    assert connect_calls == [(":memory:", False)]
    assert connection.calls == [
        (
            "ATTACH 'quack://groupsum-duckdb:9494' AS \"remote\" "
            "(TYPE QUACK, TOKEN 'secret-token')",
            None,
        ),
        ('USE "remote"', None),
    ]
    assert engine == {
        "kind": "duckdb",
        "path": ":memory:",
        "read_only": False,
        "dsn": "quack://groupsum-duckdb:9494",
        "catalog": "remote",
    }


@pytest.mark.asyncio
async def test_default_duckdb_engine_uses_concrete_engine_session(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "default.duckdb"
    engine, maker = duckdb_engine(mapping={"kind": "duckdb", "path": str(db_path)})

    assert engine.dialect.name == "duckdb"

    session = maker()
    try:
        assert isinstance(session, EngineSession)
        await session.execute(
            text("CREATE TABLE direct_rows (id VARCHAR, name VARCHAR)")
        )
        await session.executemany(
            text("INSERT INTO direct_rows VALUES (:id, :name)"),
            ({"id": "a", "name": "alpha"}, {"id": "b", "name": "beta"}),
        )
        await session.commit()
    finally:
        await session.close()

    session = maker()
    try:
        rows = (
            await session.execute(text("SELECT id, name FROM direct_rows ORDER BY id"))
        ).all()
    finally:
        await session.close()

    assert rows == [("a", "alpha"), ("b", "beta")]


@pytest.mark.asyncio
async def test_app_initialize_runs_ddl_with_duckdb_engine_spec(tmp_path: Path) -> None:
    class DuckDbInitializedWidget(TableBase):
        __tablename__ = "duckdb_engine_initialized_widgets"
        __allow_unmapped__ = True

        id = Column(String, primary_key=True)
        name = Column(String, nullable=False)

    db_path = tmp_path / "ddl.duckdb"
    app = TigrblApp.from_spec(
        AppSpec(
            engine={
                "kind": "duckdb",
                "path": str(db_path),
                "name": "duckdb_ddl",
            },
            tables=(DuckDbInitializedWidget,),
        )
    )

    initialized = app.initialize()
    if inspect.isawaitable(initialized):
        await initialized

    provider = resolver.resolve_provider(engine_name="duckdb_ddl")
    assert provider is not None
    session = provider.session()
    try:
        assert isinstance(session, EngineSession)
        await session.executemany(
            text(
                "INSERT INTO duckdb_engine_initialized_widgets "
                "(id, name) VALUES (:id, :name)"
            ),
            ({"id": "w1", "name": "widget one"},),
        )
        await session.commit()
        rows = (
            await session.execute(
                text(
                    "SELECT id, name FROM duckdb_engine_initialized_widgets ORDER BY id"
                )
            )
        ).all()
    finally:
        await session.close()

    assert rows == [("w1", "widget one")]


@pytest.mark.asyncio
async def test_native_duckdb_mode_preserves_tigrbl_session_operations(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "native.duckdb"
    engine, maker = duckdb_engine(
        mapping={"kind": "duckdb", "path": str(db_path), "mode": "native"}
    )

    assert engine == {
        "kind": "duckdb",
        "path": str(db_path),
        "read_only": False,
    }

    session = maker()
    try:
        assert isinstance(session, DuckDBSession)
        await session.begin()
        await session.execute(
            'CREATE TABLE "duckdb_engine_native_widgets" '
            '("id" VARCHAR PRIMARY KEY, "name" VARCHAR NOT NULL)'
        )
        obj = DuckDbNativeWidget()
        obj.id = "n1"
        obj.name = "native one"
        session.add(obj)
        await session.commit()

        fetched = await session.get(DuckDbNativeWidget, "n1")
        assert fetched is not None
        assert fetched.name == "native one"

        await session.begin()
        await session.delete(fetched)
        await session.commit()

        assert await session.get(DuckDbNativeWidget, "n1") is None
    finally:
        await session.close()
