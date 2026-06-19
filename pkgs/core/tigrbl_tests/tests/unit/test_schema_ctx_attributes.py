import pytest
from pydantic import BaseModel

from tigrbl import schema_ctx
from tigrbl import build_schemas
from tigrbl import TableBase


def test_schema_ctx_records_alias() -> None:
    class Model:
        @schema_ctx(alias="Foo", kind="out")
        class FooOut(BaseModel):
            id: int

    decl = Model.FooOut.__tigrbl_schema_decl__
    assert decl.alias == "Foo"


def test_schema_ctx_registers_alias_namespace() -> None:
    class Model:
        @schema_ctx(alias="Foo", kind="out")
        class FooOut(BaseModel):
            id: int

    build_schemas(Model, [])
    assert hasattr(Model.schemas, "Foo")


def test_schema_ctx_table_local_schema_is_available_before_build() -> None:
    class Widget(TableBase):
        @schema_ctx(alias="Search", kind="in")
        class SearchIn(BaseModel):
            q: str

        @schema_ctx(alias="Search", kind="out")
        class SearchOut(BaseModel):
            id: int

    assert Widget.schemas.Search.in_ is Widget.SearchIn
    assert Widget.schemas.Search.out is Widget.SearchOut


def test_schema_ctx_records_kind_in() -> None:
    class Model:
        @schema_ctx(alias="Bar", kind="in")
        class BarIn(BaseModel):
            id: int

    decl = Model.BarIn.__tigrbl_schema_decl__
    assert decl.kind == "in"


def test_schema_ctx_records_kind_out() -> None:
    class Model:
        @schema_ctx(alias="Bar", kind="out")
        class BarOut(BaseModel):
            id: int

    decl = Model.BarOut.__tigrbl_schema_decl__
    assert decl.kind == "out"


def test_schema_ctx_assigns_in_model() -> None:
    class Model:
        @schema_ctx(alias="Bar", kind="in")
        class BarIn(BaseModel):
            id: int

    build_schemas(Model, [])
    assert Model.schemas.Bar.in_ is Model.BarIn


def test_schema_ctx_assigns_out_model() -> None:
    class Model:
        @schema_ctx(alias="Bar", kind="out")
        class BarOut(BaseModel):
            id: int

    build_schemas(Model, [])
    assert Model.schemas.Bar.out is Model.BarOut


def test_schema_ctx_invalid_kind_raises_value_error() -> None:
    class Dummy:
        pass

    with pytest.raises(ValueError):

        @schema_ctx(alias="Bad", kind="sideways", for_=Dummy)
        class BadSchema(BaseModel):
            pass


def test_schema_ctx_explicit_for_registration() -> None:
    class Target:
        pass

    @schema_ctx(alias="Ext", kind="out", for_=Target)
    class ExtSchema(BaseModel):
        id: int

    assert Target.schemas.Ext.out is ExtSchema

    build_schemas(Target, [])
    assert Target.schemas.Ext.out is ExtSchema


def test_schema_ctx_build_preserves_auto_bound_table_schema() -> None:
    class Target(TableBase):
        @schema_ctx(alias="Ext", kind="out")
        class ExtSchema(BaseModel):
            id: int

    assert Target.schemas.Ext.out is Target.ExtSchema

    build_schemas(Target, [])
    assert Target.schemas.Ext.out is Target.ExtSchema


def test_schema_ctx_non_class_target_raises_type_error() -> None:
    with pytest.raises(TypeError):

        @schema_ctx(alias="Bad", kind="out")
        def not_a_class():
            pass
