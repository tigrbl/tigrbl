from __future__ import annotations

from sqlalchemy import String

from tigrbl_base._base._column_base import ColumnBase
from tigrbl_core._spec import ColumnSpec, DataTypeSpec, FieldSpec, StorageSpec


def test_column_base_lowers_datatype_when_storage_type_missing() -> None:
    spec = ColumnSpec(
        storage=StorageSpec(type_=None),
        datatype=DataTypeSpec(logical_name="string", options={"max_length": 32}),
        field=FieldSpec(py_type=str, constraints={"max_length": 32}),
    )
    column = ColumnBase(spec=spec)
    assert isinstance(column.storage, StorageSpec)
    assert column.datatype.logical_name == "string"
    assert isinstance(column.type, String)
    assert column.type.length == 32
