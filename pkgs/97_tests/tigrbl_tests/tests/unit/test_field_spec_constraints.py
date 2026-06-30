import pytest
from pydantic import ValidationError
from pydantic.errors import PydanticUserError

from tigrbl._spec import ColumnSpec, F, IO
from tigrbl_core.schema.builder.build_schema import _build_schema


def _virtual_spec(field: F) -> ColumnSpec:
    return ColumnSpec(
        storage=None,
        field=field,
        io=IO(in_verbs=("create",), out_verbs=("read",)),
    )


def test_f_constraints_support_string_validation_and_schema_metadata():
    class ConstraintModel:
        __tigrbl_cols__ = {
            "code": _virtual_spec(
                F(
                    py_type=str,
                    constraints={
                        "min_length": 2,
                        "max_length": 4,
                        "pattern": "^[A-Z]+$",
                        "examples": ["AB"],
                    },
                    description="Uppercase code",
                    required_in=("create",),
                )
            )
        }

    schema = _build_schema(ConstraintModel, verb="create")

    assert schema.model_validate({"code": "ABCD"}).code == "ABCD"
    field_schema = schema.model_json_schema()["properties"]["code"]
    string_schema = next(
        branch for branch in field_schema["anyOf"] if branch.get("type") == "string"
    )
    assert string_schema["minLength"] == 2
    assert string_schema["maxLength"] == 4
    assert string_schema["pattern"] == "^[A-Z]+$"
    assert field_schema["description"] == "Uppercase code"
    assert field_schema["examples"] == ["AB"]

    with pytest.raises(ValidationError):
        schema.model_validate({"code": "a"})


def test_f_constraints_support_numeric_bounds_and_multiples():
    class NumericConstraintModel:
        __tigrbl_cols__ = {
            "quantity": _virtual_spec(
                F(
                    py_type=int,
                    constraints={"ge": 2, "le": 10, "multiple_of": 2},
                    required_in=("create",),
                )
            )
        }

    schema = _build_schema(NumericConstraintModel, verb="create")

    assert schema.model_validate({"quantity": 8}).quantity == 8

    for invalid in (1, 11, 3):
        with pytest.raises(ValidationError):
            schema.model_validate({"quantity": invalid})


def test_f_constraints_reject_removed_regex_keyword():
    class RegexConstraintModel:
        __tigrbl_cols__ = {
            "code": _virtual_spec(
                F(py_type=str, constraints={"regex": "^[A-Z]+$"})
            )
        }

    with pytest.raises(PydanticUserError, match="regex.*removed"):
        _build_schema(RegexConstraintModel, verb="create")


def test_f_constraints_reject_removed_unique_items_keyword():
    class UniqueItemsConstraintModel:
        __tigrbl_cols__ = {
            "tags": _virtual_spec(
                F(py_type=list[str], constraints={"unique_items": True})
            )
        }

    with pytest.raises(PydanticUserError, match="unique_items.*removed"):
        _build_schema(UniqueItemsConstraintModel, verb="create")
