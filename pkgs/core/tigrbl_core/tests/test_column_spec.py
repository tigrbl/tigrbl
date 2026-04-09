from __future__ import annotations

from sqlalchemy import Column, Integer, String

from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec


def test_column_spec_defaults_field_and_io_when_not_provided() -> None:
    spec = ColumnSpec(storage=None)

    assert isinstance(spec.field, FieldSpec)
    assert isinstance(spec.io, IOSpec)


def test_column_spec_stores_custom_factories() -> None:
    def make_default(ctx: dict) -> str:
        return f"x-{ctx['id']}"

    def make_read(obj: object, ctx: dict) -> str:
        _ = obj
        return ctx["value"]

    spec = ColumnSpec(
        storage=None, default_factory=make_default, read_producer=make_read
    )

    assert spec.default_factory is make_default
    assert spec.read_producer is make_read


def test_column_spec_collect_reads_declared_mappings() -> None:
    class Demo:
        __tigrbl_colspecs__ = {"name": ColumnSpec(storage=None)}

    collected = ColumnSpec.collect(Demo)

    assert "name" in collected


def test_column_spec_mro_collect_columns_aliases_collect() -> None:
    class Demo:
        __tigrbl_cols__ = {"title": ColumnSpec(storage=None)}

    assert ColumnSpec.mro_collect_columns(Demo) == ColumnSpec.collect(Demo)


def test_column_spec_collect_preserves_storage_metadata_from_plain_columns() -> None:
    class Demo:
        name = Column(String(32), nullable=False)
        age = Column(Integer, nullable=True)

    collected = ColumnSpec.collect(Demo)

    assert collected["name"].storage is not None
    assert collected["name"].storage.nullable is False
    assert collected["name"].storage.type_ is not None
    assert collected["name"].storage.physical_type is not None
    assert collected["name"].storage.physical_type.physical_name.lower() in {"string", "varchar"}
