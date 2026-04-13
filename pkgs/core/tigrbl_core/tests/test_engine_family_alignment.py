from __future__ import annotations

from tigrbl_core._spec import DataTypeSpec, EngineDatatypeBridge
from tigrbl_core._spec.datatypes import infer_datatype


def test_engine_family_alignment_normalizes_common_scalar_inputs() -> None:
    assert infer_datatype(field_py_type=str).logical_name == "string"
    assert infer_datatype(field_py_type=int).logical_name == "integer"
    assert infer_datatype(field_py_type=float).logical_name == "number"
    assert infer_datatype(field_py_type=bool).logical_name == "boolean"


def test_engine_family_alignment_exposes_distinct_lowering_matrices() -> None:
    bridge = EngineDatatypeBridge()
    datatype = DataTypeSpec(logical_name="json")

    assert bridge.lower("sqlite", datatype).physical_name == "JSON"
    assert bridge.lower("postgres", datatype).physical_name == "JSONB"
    assert bridge.lower("cache", datatype).physical_name == "json"
