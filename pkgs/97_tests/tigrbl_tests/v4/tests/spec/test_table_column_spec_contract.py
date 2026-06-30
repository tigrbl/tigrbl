from __future__ import annotations

import datetime as dt

import pytest
from sqlalchemy import Integer, String

from tigrbl import (
    ColumnSpec,
    FieldSpec,
    ForeignKeySpec,
    IOSpec,
    StorageSpec,
    TableSpec,
)


def test_tablespec_model_ref_is_portable_without_model_import() -> None:
    table = TableSpec(model_ref="pkg.models:Book", portability_class="portable")

    assert table.model_ref == "pkg.models:Book"
    assert table.model == "pkg.models:Book"
    assert table.portability_class == "portable"


def test_tablespec_rejects_string_column_entries() -> None:
    with pytest.raises(TypeError, match="columns entries must be nested column specs"):
        TableSpec.from_dict({"model_ref": "pkg.models:Book", "columns": ["title"]})


def test_columnspec_keeps_storage_field_and_io_metadata_separate() -> None:
    storage = StorageSpec(type_=String(80), nullable=False, index=True)
    field = FieldSpec(
        py_type=str,
        description="Book title",
        constraints={"min_length": 1, "max_length": 80},
        required_in=("create",),
    )
    io = IOSpec(
        in_verbs=("create", "update"),
        out_verbs=("read", "list"),
        mutable_verbs=("update",),
        alias_in="bookTitle",
        alias_out="bookTitle",
        filter_ops=("eq", "ilike"),
        sortable=True,
    )

    column = ColumnSpec(storage=storage, field=field, io=io)

    assert column.storage is storage
    assert column.field is field
    assert column.io is io
    assert column.storage.nullable is False
    assert column.field.required_in == ("create",)
    assert column.io.alias_in == "bookTitle"
    assert not hasattr(column.storage, "required_in")
    assert not hasattr(column.field, "index")


def test_storagespec_preserves_foreign_key_physical_metadata() -> None:
    fk = ForeignKeySpec(
        target="author.id",
        on_delete="RESTRICT",
        on_update="CASCADE",
        deferrable=True,
        initially_deferred=True,
        match="SIMPLE",
    )
    storage = StorageSpec(
        type_=Integer,
        nullable=False,
        index=True,
        fk=fk,
        check="author_id > 0",
    )

    assert storage.fk is fk
    assert storage.fk.target == "author.id"
    assert storage.fk.on_update == "CASCADE"
    assert storage.fk.deferrable is True
    assert storage.check == "author_id > 0"


def test_fieldspec_semantic_metadata_is_storage_independent() -> None:
    field = FieldSpec(
        py_type=dt.datetime,
        description="Created timestamp",
        constraints={"timezone": True},
        required_in=("create",),
        allow_null_in=("update",),
    )

    assert field.py_type is dt.datetime
    assert field.constraints == {"timezone": True}
    assert field.required_in == ("create",)
    assert field.allow_null_in == ("update",)
    assert not hasattr(field, "nullable")


def test_iospec_verb_visibility_alias_filter_and_sort_contract() -> None:
    io = IOSpec(
        in_verbs=("create", "update"),
        out_verbs=("read", "list", "create"),
        mutable_verbs=("update",),
        alias_in="authorId",
        alias_out="authorId",
        filter_ops=("eq", "in"),
        sortable=True,
    )

    assert "create" in io.in_verbs
    assert "read" in io.out_verbs
    assert io.mutable_verbs == ("update",)
    assert io.alias_in == io.alias_out == "authorId"
    assert io.filter_ops == ("eq", "in")
    assert io.sortable is True


def test_columnspec_infers_datatype_from_field_and_storage() -> None:
    column = ColumnSpec(
        storage=StorageSpec(type_=String(32), nullable=False),
        field=FieldSpec(py_type=str, constraints={"max_length": 32}),
        io=IOSpec(out_verbs=("read",)),
    )

    assert column.datatype is not None
    assert column.datatype.logical_name == "string"
    assert column.datatype.nullable is False
    assert column.datatype.options == {"max_length": 32}
