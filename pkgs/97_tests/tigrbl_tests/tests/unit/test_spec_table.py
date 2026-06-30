from tests.conftest import mro_collect_table_spec
from tigrbl.factories.table import defineTableSpec, deriveTableSpec
from tigrbl_concrete.factories.table import (
    defineTableSpec as concrete_defineTableSpec,
    deriveTableSpec as concrete_deriveTableSpec,
)
from tigrbl_concrete.factories import deriveTableSpec as concrete_package_deriveTableSpec


class BaseSpec(defineTableSpec(engine="sqlite://:memory:", ops=("create",))):
    __tablename__ = "widgets"


class Widget(BaseSpec):
    OPS = ("read",)
    COLUMNS = ("id", "name")


class ConcreteSpecBase(defineTableSpec(engine="sqlite:///:memory:", ops=("create",))):
    __tablename__ = "widgets_concrete"


class ConcreteWidget(ConcreteSpecBase):
    OPS = ("read",)


def test_table_spec_defaults_and_merge():
    spec = mro_collect_table_spec(Widget)
    assert spec.model is Widget
    assert spec.engine == "sqlite://:memory:"
    assert spec.ops == ("read", "create")
    assert spec.columns == ("id", "name")
    assert spec.schemas == ()
    assert spec.hooks == ()


def test_concrete_table_initializes_from_mro_collect_spec():
    assert ConcreteWidget.OPS == ("read", "create")
    assert ConcreteWidget.table_config["engine"] == "sqlite:///:memory:"


def test_derive_table_spec_exports_collected_spec():
    spec = deriveTableSpec(Widget)
    assert spec.model is Widget
    assert spec.engine == "sqlite://:memory:"
    assert spec.ops == ("read", "create")
    assert spec.columns == ("id", "name")


def test_table_factory_facade_reexports_concrete_functions():
    assert defineTableSpec is concrete_defineTableSpec
    assert deriveTableSpec is concrete_deriveTableSpec
    assert concrete_package_deriveTableSpec is concrete_deriveTableSpec

