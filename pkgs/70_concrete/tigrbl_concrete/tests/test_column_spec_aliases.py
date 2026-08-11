from tigrbl_concrete._concrete import Column, RestBulkCrudTable
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec
from tigrbl_core._spec.storage_spec import StorageSpec


def test_column_exposes_canonical_spec_constructors() -> None:
    assert Column.S is StorageSpec
    assert Column.F is FieldSpec
    assert Column.IO is IOSpec


def test_table_maps_column_from_specs_without_sqlalchemy_declarations() -> None:
    class ColumnSpecAliasWidget(RestBulkCrudTable):
        __tablename__ = "column_spec_alias_widgets"

        id = Column(
            storage=Column.S(primary_key=True, nullable=False),
            field=Column.F(py_type=str, constraints={"max_length": 64}),
            io=Column.IO(out_verbs=("read", "list")),
        )
        quantity = Column(
            storage=Column.S(nullable=False),
            field=Column.F(py_type=int, required_in=("create",)),
            io=Column.IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
                filter_ops=("eq", "gte", "lte"),
                sortable=True,
            ),
        )

    assert tuple(ColumnSpecAliasWidget.__table__.columns.keys()) == ("id", "quantity")
    assert ColumnSpecAliasWidget.id.storage.primary_key is True
    assert ColumnSpecAliasWidget.quantity.field.py_type is int
    assert ColumnSpecAliasWidget.quantity.io.sortable is True
