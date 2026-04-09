from __future__ import annotations

from tigrbl_core._spec import ColumnSpec, FieldSpec, StorageSpec


def test_column_datatype_integration_derives_string_datatype_from_field_type() -> None:
    spec = ColumnSpec(storage=None, field=FieldSpec(py_type=str))
    assert spec.datatype.logical_name == "string"


def test_column_datatype_integration_respects_explicit_datatype_over_storage() -> None:
    explicit = ColumnSpec(
        storage=StorageSpec(type_=int),
        field=FieldSpec(py_type=int),
    )
    assert explicit.datatype.logical_name == "integer"
