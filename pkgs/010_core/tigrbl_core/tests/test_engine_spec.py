from __future__ import annotations

import pytest

from tigrbl_core._spec.engine_spec import EngineProviderSpec, EngineSpec


def test_from_any_parses_sqlite_and_postgres_dsn() -> None:
    sqlite = EngineSpec.from_any("sqlite://:memory:")
    pg = EngineSpec.from_any("postgresql://user:pwd@localhost:5432/db")

    assert sqlite is not None and sqlite.kind == "sqlite" and sqlite.memory is True
    assert pg is not None and pg.kind == "postgres" and pg.async_ is False


def test_from_any_parses_mapping_aliases() -> None:
    spec = EngineSpec.from_any(
        {
            "engine": "postgres",
            "async": True,
            "password": "pw",
            "db": "app",
            "max_size": "11",
        }
    )

    assert spec is not None
    assert spec.kind == "postgres"
    assert spec.async_ is True
    assert spec.pwd == "pw"
    assert spec.name == "app"
    assert spec.max == 11


def test_from_any_rejects_unknown_dsn() -> None:
    with pytest.raises(ValueError, match="Unsupported DSN"):
        EngineSpec.from_any("oracle://local")


def test_from_any_parses_duckdb_file_and_quack_dsn() -> None:
    file_spec = EngineSpec.from_any("data/analytics.duckdb")
    quack_spec = EngineSpec.from_any("quack://data/analytics.duckdb")
    compact_quack_spec = EngineSpec.from_any("quack:data:9494")

    assert file_spec is not None
    assert file_spec.kind == "duckdb"
    assert file_spec.dsn == "data/analytics.duckdb"
    assert quack_spec is not None
    assert quack_spec.kind == "duckdb"
    assert quack_spec.dsn == "quack://data/analytics.duckdb"
    assert compact_quack_spec is not None
    assert compact_quack_spec.kind == "duckdb"
    assert compact_quack_spec.dsn == "quack:data:9494"


def test_build_requires_registered_engine_provider(monkeypatch) -> None:
    from tigrbl_core._spec import plugins, registry

    monkeypatch.setattr(plugins, "load_engine_plugins", lambda: None)
    registry._ENGINE_REGISTRY.clear()

    with pytest.raises(RuntimeError, match="Unknown or unavailable engine kind"):
        EngineSpec(kind="sqlite", async_=False, memory=False, path="db.sqlite").build()


def test_provider_from_any_wraps_spec_property() -> None:
    inner = EngineSpec(kind="sqlite", memory=True)

    class Obj:
        spec = inner

    provider = EngineProviderSpec.from_any(Obj())

    assert provider is not None
    assert provider.spec is inner


def test_from_any_accepts_engine_like_spec_object() -> None:
    class ForeignSpec:
        kind = "sqlite"
        async_ = False
        dsn = None
        path = None
        memory = True
        pool = None
        user = None
        pwd = None
        host = None
        port = None
        name = None
        pool_size = 10
        max = 20

    class ForeignEngine:
        spec = ForeignSpec()

    parsed = EngineSpec.from_any(ForeignEngine())

    assert parsed is not None
    assert parsed.kind == "sqlite"
    assert parsed.memory is True


def test_repr_redacts_passwords() -> None:
    spec = EngineSpec(
        kind="postgres",
        dsn="postgresql://alice:secret@localhost:5432/db",
        mapping={"password": "secret", "name": "db"},
    )

    rendered = repr(spec)

    assert "secret" not in rendered
    assert "***" in rendered


def test_repr_redacts_quack_token() -> None:
    spec = EngineSpec.from_any(
        {
            "kind": "duckdb",
            "dsn": "quack://analytics.internal:9494",
            "token": "quack-secret-token",
        }
    )

    assert spec is not None
    rendered = repr(spec)

    assert "quack-secret-token" not in rendered
    assert "***" in rendered
