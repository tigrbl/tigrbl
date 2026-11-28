from __future__ import annotations

from tigrbl_core._spec.column_spec import ColumnSpec
from tigrbl_core._spec.field_spec import FieldSpec
from tigrbl_core._spec.io_spec import IOSpec, Pair
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.storage_spec import StorageSpec

from tigrbl_kernel._compile import _compile_opview_from_specs


def test_compile_opview_from_specs_builds_in_out_and_stored_schema_metadata() -> None:
    columns = {
        "id": ColumnSpec(
            storage=StorageSpec(type_=int, nullable=False),
            field=FieldSpec(py_type=int, required_in=("create",)),
            io=IOSpec(in_verbs=("create",), out_verbs=("create",)),
        ),
        "display_name": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=True),
            field=FieldSpec(py_type=str, constraints={"max_length": 32}),
            io=IOSpec(
                in_verbs=("create",),
                out_verbs=("create",),
                alias_in="displayName",
                alias_out="displayName",
            ),
        ),
        "computed": ColumnSpec(
            storage=None,
            field=FieldSpec(py_type=str),
            io=IOSpec(in_verbs=("create",), out_verbs=("create",)),
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_in.fields == ("computed", "display_name", "id")
    assert opview.schema_out.fields == ("computed", "display_name", "id")
    assert opview.schema_stored is not None
    assert opview.schema_stored.fields == ("display_name", "id")
    assert opview.schema_in.by_field["id"]["required"] is True
    assert opview.schema_in.by_field["id"]["py_type"] is int
    assert opview.schema_in.by_field["display_name"]["alias_in"] == "displayName"
    assert opview.schema_in.by_field["display_name"]["max_length"] == 32
    assert opview.schema_out.by_field["display_name"]["alias_out"] == "displayName"
    assert opview.schema_in.by_field["computed"]["virtual"] is True
    assert opview.schema_out.by_field["computed"]["virtual"] is True
    assert opview.schema_stored.by_field["id"]["required_from_client"] is True
    assert opview.schema_stored.by_field["display_name"]["from_client"] is True


def test_compile_opview_from_specs_adds_header_and_py_type_metadata() -> None:
    columns = {
        "request_id": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=False),
            field=FieldSpec(py_type=str, required_in=("create",)),
            io=IOSpec(
                in_verbs=("create",),
                out_verbs=("create",),
                header_in="X-Request-Id",
                header_required_in=True,
            ),
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_in.by_field["request_id"]["header_in"] == "X-Request-Id"
    assert opview.schema_in.by_field["request_id"]["header_required_in"] is True
    assert opview.schema_out.by_field["request_id"]["py_type"] == "str"
    assert opview.schema_stored is not None
    assert opview.schema_stored.by_field["request_id"]["py_type"] is str


def test_compile_opview_from_specs_requires_non_nullable_create_storage() -> None:
    columns = {
        "label": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=False),
            field=FieldSpec(py_type=str),
            io=IOSpec(in_verbs=("create",), out_verbs=("read",)),
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_in.by_field["label"]["required"] is True
    assert opview.schema_stored is not None
    assert opview.schema_stored.by_field["label"]["required"] is True


def test_compile_opview_from_specs_uses_target_verb_for_alias_bound_ops() -> None:
    columns = {
        "name": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=False),
            field=FieldSpec(py_type=str, required_in=("create",)),
            io=IOSpec(in_verbs=("create",), out_verbs=("create",)),
        ),
    }
    op_spec = OpSpec(alias="BenchmarkItem.create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_in.fields == ("name",)
    assert opview.schema_in.by_field["name"]["required"] is True
    assert opview.schema_stored is not None
    assert opview.schema_stored.fields == ("name",)


def test_compile_opview_from_specs_marks_server_default_stored_fields_not_client_required() -> None:
    columns = {
        "created_at": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=False, server_default="now()"),
            field=FieldSpec(py_type=str),
            io=IOSpec(out_verbs=("create",)),
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_stored is not None
    assert opview.schema_stored.fields == ("created_at",)
    assert opview.schema_stored.required_from_client == ()
    assert opview.schema_stored.by_field["created_at"]["server_default"] is True
    assert opview.schema_stored.by_field["created_at"]["required"] is False


def test_compile_opview_from_specs_includes_paired_fields_in_stored_shape() -> None:
    io = IOSpec().paired(
        lambda _ctx: Pair(raw="cleartext", stored="digest:cleartext"),
        alias="token_raw",
        verbs=("create",),
    )
    columns = {
        "token": ColumnSpec(
            storage=StorageSpec(type_=str, nullable=False),
            field=FieldSpec(py_type=str),
            io=io,
        ),
    }
    op_spec = OpSpec(alias="create", target="create")

    opview = _compile_opview_from_specs(self=None, specs=columns, sp=op_spec)

    assert opview.schema_stored is not None
    assert opview.schema_stored.fields == ("token",)
    assert opview.schema_stored.by_field["token"]["derived"] is True
    assert opview.schema_stored.by_field["token"]["required"] is True
