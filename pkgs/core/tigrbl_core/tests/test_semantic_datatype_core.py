from __future__ import annotations

from tigrbl_core._spec import DataTypeSpec, StorageTypeRef
from tigrbl_core._spec.datatypes import infer_datatype


def test_semantic_datatype_core_infers_string_and_preserves_constraints() -> None:
    spec = infer_datatype(field_py_type=str, constraints={"max_length": 64})
    assert spec.logical_name == "string"
    assert spec.options["max_length"] == 64


def test_storage_type_ref_round_trips_with_engine_kind() -> None:
    ref = StorageTypeRef(engine_kind="sqlite", physical_name="TEXT")
    restored = StorageTypeRef.from_json(ref.to_json())
    assert restored == ref


def test_datatype_spec_new_uses_options_and_nullable() -> None:
    spec = DataTypeSpec.new("uuid", nullable=True, format="canonical")
    assert spec.logical_name == "uuid"
    assert spec.nullable is True
    assert spec.options["format"] == "canonical"
