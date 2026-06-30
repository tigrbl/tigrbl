from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
from sqlalchemy import String

import tigrbl
from tigrbl_base._base import AppBase, ColumnBase, ForeignKeyBase, RouterBase
from tigrbl_base._base import SchemaBase, TableBase
from tigrbl_base._base import StorageTransformBase
from tigrbl_base._base import TableRegistryBase
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.storage_spec import StorageSpec


PUBLIC_BASE_PROJECTIONS = (
    "AppBase",
    "ForeignKeyBase",
    "RouterBase",
    "TableBase",
    "TableRegistryBase",
)

INTERNAL_BASE_SYMBOLS = {
    "AliasBase",
    "BindingBase",
    "BindingRegistryBase",
    "ColumnBase",
    "SchemaBase",
    "StorageTransformBase",
}


def test_public_base_projection_is_exact_and_reload_stable() -> None:
    reloaded = importlib.reload(tigrbl)
    base = importlib.import_module("tigrbl_base._base")

    for symbol in PUBLIC_BASE_PROJECTIONS:
        assert symbol in reloaded.__all__
        assert getattr(reloaded, symbol) is getattr(base, symbol)

    for symbol in INTERNAL_BASE_SYMBOLS:
        assert symbol not in reloaded.__all__
        assert not hasattr(reloaded, symbol)


def test_app_base_bind_spec_does_not_share_mutable_sequences() -> None:
    source_routers = ["api"]
    source_tables = ["user"]
    source = AppSpec(routers=source_routers, tables=source_tables)

    bound = AppBase.bind_spec(source)
    source_routers.append("admin")
    source_tables.append("group")

    assert bound.routers == ("api",)
    assert bound.tables == ("user",)


def test_router_base_include_tables_delegates_each_table_with_base_prefix() -> None:
    calls: list[tuple[type, str | None, bool]] = []

    class Router(RouterBase):
        def _include_table_impl(
            self,
            table: type,
            *,
            app: object | None = None,
            prefix: str | None = None,
            mount_router: bool = True,
        ) -> tuple[type, object]:
            calls.append((table, prefix, mount_router))
            return table, SimpleNamespace(table=table, app=app, prefix=prefix)

    class User:
        pass

    class Group:
        pass

    app = object()
    included = Router().include_tables(
        [User, Group],
        app=app,
        base_prefix="/v1",
        mount_router=False,
    )

    assert list(included) == ["User", "Group"]
    assert included["User"].app is app
    assert calls == [(User, "/v1", False), (Group, "/v1", False)]


def test_table_base_column_metadata_isolated_across_subclasses() -> None:
    class Account(TableBase):
        id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))
        name = ColumnBase(storage=StorageSpec(type_=String, nullable=False))

    class Team(TableBase):
        id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))

    assert set(Account.__tigrbl_cols__) == {"id", "name"}
    assert set(Team.__tigrbl_cols__) == {"id"}
    assert Account.__tigrbl_cols__ is not Team.__tigrbl_cols__
    assert Account.__tablename__ == "account"
    assert Team.__tablename__ == "team"


def test_table_registry_base_lookup_is_deterministic_for_alias_and_model_name() -> None:
    class User(TableBase):
        id = ColumnBase(storage=StorageSpec(type_=String, primary_key=True))

    registry = TableRegistryBase([("subject", User)])

    assert list(registry) == ["subject", "User"]
    assert registry["subject"] is User
    assert registry["User"] is User
    assert registry.User is User.__table__


def test_schema_base_collect_ignores_malformed_declarations() -> None:
    class Declared:
        __tigrbl_schema_decl__ = SimpleNamespace(alias="item", kind="out")

    class Model:
        schemas = {"bad": object(), "good": {"in": int}}
        nested = Declared
        not_a_schema = object()

    assert SchemaBase.collect(Model) == {
        "good": {"in": int},
        "item": {"out": Declared},
    }


def test_storage_base_contracts_are_immutable_and_callable_preserving() -> None:
    def to_stored(value: str, ctx: dict) -> str:
        return value.strip()

    transform = StorageTransformBase(to_stored=to_stored)
    fk = ForeignKeyBase(target="account(id)", on_delete="CASCADE")

    assert transform.to_stored is to_stored
    assert fk.target == "account(id)"
    with pytest.raises(Exception):
        fk.target = "team(id)"  # type: ignore[misc]
