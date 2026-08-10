from __future__ import annotations

from tigrbl import AppSpec, Column, Op, Table, TableSpec, TigrblApp
from tigrbl.factories import (
    activateTableSpec,
    defineAppSpec,
    defineTableSpec,
    deriveApp,
    deriveTableSpec,
    makeColumn,
    makeOp,
    provideTableSpec,
)


class Widget:
    OPS = ("read",)
    COLUMNS = ("id",)


def test_make_functional_and_classmethod_forms() -> None:
    assert isinstance(makeColumn(), Column)
    assert isinstance(Column.make(), Column)
    assert makeOp(alias="inspect").alias == Op.make(alias="inspect").alias


def test_define_functional_and_classmethod_forms() -> None:
    assert issubclass(defineAppSpec(title="Inventory"), AppSpec)
    assert issubclass(TigrblApp.define(title="Inventory"), AppSpec)
    assert issubclass(defineTableSpec(ops=("create",)), TableSpec)
    assert issubclass(Table.define(ops=("create",)), TableSpec)


def test_derive_functional_and_classmethod_forms() -> None:
    assert issubclass(deriveApp(title="Inventory"), TigrblApp)
    assert issubclass(TigrblApp.derive(title="Inventory"), TigrblApp)

    definition = Table.define(ops=("create",))
    functional = deriveTableSpec(Widget, spec=definition, ops=("inspect",))
    classmethod = Table.derive(Widget, spec=definition, ops=("inspect",))
    assert functional.ops == classmethod.ops == ("read", "create", "inspect")


def test_provide_functional_and_classmethod_forms() -> None:
    table_spec = Table.derive(Widget)
    assert provideTableSpec(table_spec) is table_spec
    assert Table.provide(table_spec) is table_spec


def test_activate_functional_and_classmethod_forms(monkeypatch) -> None:
    table_spec = Table.derive(Widget)
    operations = (makeOp(alias="inspect"),)
    monkeypatch.setattr(
        "tigrbl_concrete._mapping.model.rebind", lambda model: operations
    )
    assert activateTableSpec(table_spec) == operations
    assert Table.activate(table_spec) == operations


def test_specs_are_inputs_not_factory_receivers() -> None:
    for name in ("make", "define", "derive", "provide", "activate"):
        assert name not in TableSpec.__dict__
