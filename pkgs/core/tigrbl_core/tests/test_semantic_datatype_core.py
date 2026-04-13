from __future__ import annotations

from tigrbl_core._spec import CANONICAL_DATATYPES, DataTypeSpec, StorageTypeRef, TypeRegistry
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


def test_semantic_datatype_core_normalizes_builtin_aliases() -> None:
    spec = infer_datatype(field_py_type="varchar")
    assert spec.logical_name == "string"


def test_semantic_datatype_core_registry_exposes_builtin_names() -> None:
    registry = TypeRegistry()
    assert set(CANONICAL_DATATYPES).issubset(set(registry.registered_names()))
