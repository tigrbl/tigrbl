from __future__ import annotations

import inspect

import pytest

from tigrbl_concrete._concrete._column import Column
from tigrbl_concrete._concrete._op import Op
from tigrbl_concrete._concrete._router import Router
from tigrbl_concrete._concrete._table import Table
from tigrbl_concrete._concrete.tigrbl_app import TigrblApp
from tigrbl_concrete.factories.app import defineAppSpec, deriveApp
from tigrbl_concrete.factories.column import makeColumn, makeVirtualColumn
from tigrbl_concrete.factories.op import makeOp
from tigrbl_concrete.factories.router import defineRouterSpec, deriveRouter
from tigrbl_concrete.factories.table import (
    defineTableSpec,
    deriveTableSpec,
    provideTableSpec,
)
from tigrbl_core._spec.app_spec import AppSpec
from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.router_spec import RouterSpec
from tigrbl_core._spec.table_spec import TableSpec


class Widget:
    OPS = ("read",)
    COLUMNS = ("id",)


def test_make_classmethods_match_functional_return_categories():
    assert isinstance(makeColumn(), Column)
    assert isinstance(Column.make(), Column)
    assert makeVirtualColumn().storage is None
    assert Column.make_virtual().storage is None
    assert makeOp(alias="inspect").alias == "inspect"
    assert Op.make(alias="inspect").alias == "inspect"


def test_app_and_router_classmethods_match_functional_forms():
    assert issubclass(defineAppSpec(title="Inventory"), AppSpec)
    assert issubclass(TigrblApp.define(title="Inventory"), AppSpec)
    assert issubclass(deriveApp(title="Inventory"), TigrblApp)
    assert issubclass(TigrblApp.derive(title="Inventory"), TigrblApp)

    assert issubclass(defineRouterSpec(name="inventory"), RouterSpec)
    assert issubclass(Router.define(name="inventory"), RouterSpec)
    assert issubclass(deriveRouter(name="inventory"), Router)
    assert issubclass(Router.derive(name="inventory"), Router)


def test_table_classmethods_match_functional_forms(monkeypatch):
    definition = Table.define(ops=("create",))
    assert issubclass(definition, TableSpec)

    derived = Table.derive(Widget, spec=definition, ops=("inspect",))
    assert derived.model is Widget
    assert derived.ops == ("read", "create", "inspect")
    assert Table.provide(derived) is provideTableSpec(derived)

    derived_class = Table.derive_class(Widget, ops=("create",))
    assert issubclass(derived_class, Widget)

    rebound = (makeOp(alias="inspect"),)
    monkeypatch.setattr("tigrbl_concrete._mapping.model.rebind", lambda model: rebound)
    assert Table.activate(derived) == rebound


def test_derive_table_spec_composes_without_mutating_sources():
    definition = defineTableSpec(engine="definition-engine", ops=("create",))
    source = TableSpec(model=Widget, engine="instance-engine", ops=("update",))

    from_definition = deriveTableSpec(Widget, spec=definition, ops=("inspect",))
    from_instance = deriveTableSpec(Widget, spec=source, ops=("inspect",))

    assert from_definition.engine == "definition-engine"
    assert from_definition.ops == ("read", "create", "inspect")
    assert from_instance.engine == "instance-engine"
    assert from_instance.ops == ("read", "update", "inspect")
    assert source.ops == ("update",)
    assert source.model is Widget

    with pytest.raises(TypeError, match="TableSpec instance or subclass"):
        deriveTableSpec(Widget, spec=object())  # type: ignore[arg-type]


def test_factory_bindings_are_classmethods_and_specs_remain_passive():
    for owner, names in (
        (Column, ("make", "make_virtual")),
        (Op, ("make",)),
        (TigrblApp, ("define", "derive")),
        (Router, ("define", "derive")),
        (Table, ("define", "derive", "derive_class", "provide", "activate")),
    ):
        for name in names:
            assert isinstance(inspect.getattr_static(owner, name), classmethod)

    for spec_type in (ColumnSpec, OpSpec, AppSpec, RouterSpec, TableSpec):
        for name in ("make", "define", "derive", "provide", "activate"):
            assert name not in spec_type.__dict__
