from __future__ import annotations

from typing import Literal

from tigrbl import TableBase
from tigrbl.factories.app import deriveApp
from tigrbl.factories.engine import mem, mysql, pgs
from tigrbl.factories.table import defineTableSpec, deriveTable, deriveTableSpec


EngineChoice = Literal["mem", "postgres", "mysql"]


def make_engine(choice: EngineChoice):
    """Translate application configuration into a Tigrbl engine mapping."""
    if choice == "mem":
        return mem(async_=False)
    if choice == "postgres":
        return pgs(user="app", pwd="secret", host="localhost", name="app_db")
    if choice == "mysql":
        return mysql(user="app", pwd="secret", host="localhost", name="app_db")
    raise ValueError(f"Unknown engine choice: {choice}")


class BaseWidget(TableBase):
    __tablename__ = "dynamic_engine_widgets"
    __allow_unmapped__ = True


class WidgetSpec(defineTableSpec(engine=make_engine("postgres"))):
    """Reusable configuration for widgets stored in PostgreSQL."""


class Widget(WidgetSpec, BaseWidget):
    pass


# Derivation creates a separately configured table class from the same model.
AuditWidget = deriveTable(BaseWidget, engine=make_engine("mysql"))


# Tables without their own engine binding would inherit this in-memory fallback.
App = deriveApp(
    engine=make_engine("mem"),
    tables=(Widget, AuditWidget),
)


def test_make_define_derive_engine_choice() -> None:
    app = App()

    assert App.ENGINE == make_engine("mem")
    assert deriveTableSpec(Widget).engine == make_engine("postgres")
    assert deriveTableSpec(AuditWidget).engine == make_engine("mysql")
    assert app.tables["Widget"] is Widget
    assert app.tables["BaseWidgetWithSpec"] is AuditWidget


def test_make_engine_rejects_unknown_choices() -> None:
    try:
        make_engine("oracle")  # type: ignore[arg-type]
    except ValueError as exc:
        assert str(exc) == "Unknown engine choice: oracle"
    else:
        raise AssertionError("make_engine must reject unsupported engines")
