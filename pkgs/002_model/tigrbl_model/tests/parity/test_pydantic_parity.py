"""Differential tests for the exact Pydantic surface currently used by Tigrbl."""

from __future__ import annotations

import json
from typing import Literal
from uuid import UUID

import pytest
from pydantic import (
    BaseModel as PydanticModel,
    ConfigDict as PydanticConfig,
    Field as PydanticField,
    RootModel as PydanticRoot,
    ValidationError as PydanticValidationError,
    create_model as pydantic_create_model,
)

from tigrbl_model import (
    ConfigDict,
    Field,
    Model,
    RootModel,
    ValidationError,
    create_model,
)


class PChild(PydanticModel):
    value: int


class TChild(Model):
    value: int


class PRecord(PydanticModel):
    model_config = PydanticConfig(extra="forbid", populate_by_name=True)
    name: str = PydanticField(alias="label", min_length=2)
    count: int = PydanticField(default=0, ge=0)
    child: PChild | None = None
    tags: list[str] = PydanticField(default_factory=list)
    state: Literal["ready", "done"] = "ready"


class TRecord(Model):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    name: str = Field(alias="label", min_length=2)
    count: int = Field(default=0, ge=0)
    child: TChild | None = None
    tags: list[str] = Field(default_factory=list)
    state: Literal["ready", "done"] = "ready"


@pytest.mark.parametrize(
    "payload",
    [
        {"label": "demo"},
        {"name": "demo", "count": "2"},
        {"label": "demo", "child": {"value": "3"}, "tags": ("one",)},
        {"label": "demo", "state": "done"},
    ],
)
def test_validation_and_python_dump_parity(payload) -> None:
    expected = PRecord.model_validate(payload).model_dump()
    actual = TRecord.model_validate(payload).model_dump()
    assert actual == expected


def test_dump_option_parity_for_tigrbl_call_patterns() -> None:
    payload = {
        "label": "demo",
        "count": 2,
        "child": {"value": 3},
        "tags": ["one"],
    }
    pydantic_value = PRecord.model_validate(payload)
    tigrbl_value = TRecord.model_validate(payload)
    options = [
        {"by_alias": True},
        {"exclude_none": True},
        {"exclude_unset": True},
        {"exclude_defaults": True},
        {"include": {"name", "count"}},
        {"exclude": {"child": {"value"}}},
    ]
    for option in options:
        assert tigrbl_value.model_dump(**option) == pydantic_value.model_dump(**option)

    pydantic_defaults = PRecord(label="demo")
    tigrbl_defaults = TRecord(label="demo")
    assert tigrbl_defaults.model_dump(exclude_defaults=True) == (
        pydantic_defaults.model_dump(exclude_defaults=True)
    )


def test_json_dump_and_validation_parity() -> None:
    payload = {"label": "demo", "count": 2, "child": {"value": 3}}
    pydantic_value = PRecord.model_validate(payload)
    tigrbl_value = TRecord.model_validate(payload)

    assert json.loads(tigrbl_value.model_dump_json(exclude_none=True)) == json.loads(
        pydantic_value.model_dump_json(exclude_none=True)
    )
    assert TRecord.model_validate_json(tigrbl_value.model_dump_json()).model_dump() == (
        PRecord.model_validate_json(pydantic_value.model_dump_json()).model_dump()
    )


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"label": "x"},
        {"label": "demo", "count": -1},
        {"label": "demo", "unexpected": True},
        {"label": "demo", "child": {"value": "invalid"}},
    ],
)
def test_rejected_inputs_have_parity_locations(payload) -> None:
    with pytest.raises(PydanticValidationError) as pydantic_error:
        PRecord.model_validate(payload)
    with pytest.raises(ValidationError) as tigrbl_error:
        TRecord.model_validate(payload)

    expected_locations = {tuple(item["loc"]) for item in pydantic_error.value.errors()}
    actual_locations = {tuple(item["loc"]) for item in tigrbl_error.value.errors()}
    assert actual_locations == expected_locations


def test_model_fields_required_annotation_and_defaults_parity() -> None:
    for name in PRecord.model_fields:
        expected = PRecord.model_fields[name]
        actual = TRecord.model_fields[name]
        assert actual.is_required() == expected.is_required()
        assert actual.annotation == (
            TChild | None if name == "child" else expected.annotation
        )
        if expected.default_factory is None and not expected.is_required():
            assert actual.default == expected.default


def test_construct_bypass_parity() -> None:
    expected = PRecord.model_construct(name=4, count="bad")
    actual = TRecord.model_construct(name=4, count="bad")

    with pytest.warns(UserWarning):
        expected_dump = expected.model_dump()
    assert actual.model_dump() == expected_dump
    assert actual.model_fields_set == expected.model_fields_set


def test_dynamic_create_model_parity() -> None:
    PDynamic = pydantic_create_model(
        "Dynamic",
        value=(int, PydanticField(..., ge=1)),
        note=(str | None, None),
    )
    TDynamic = create_model(
        "Dynamic", value=(int, Field(..., ge=1)), note=(str | None, None)
    )

    assert TDynamic.model_validate({"value": "2"}).model_dump() == (
        PDynamic.model_validate({"value": "2"}).model_dump()
    )
    assert TDynamic.model_json_schema() == PDynamic.model_json_schema()


def test_root_model_parity() -> None:
    PValues = PydanticRoot[list[int]]
    TValues = RootModel[list[int]]

    assert TValues.model_validate(["1", 2]).model_dump() == (
        PValues.model_validate(["1", 2]).model_dump()
    )
    assert json.loads(TValues.model_validate([1, 2]).model_dump_json()) == json.loads(
        PValues.model_validate([1, 2]).model_dump_json()
    )


def test_basic_json_schema_parity() -> None:
    PSchema = pydantic_create_model(
        "Schema",
        id=(UUID, ...),
        name=(str, PydanticField(..., min_length=2, examples=["demo"])),
        count=(int, PydanticField(default=0, ge=0)),
    )
    TSchema = create_model(
        "Schema",
        id=(UUID, ...),
        name=(str, Field(..., min_length=2, examples=["demo"])),
        count=(int, Field(default=0, ge=0)),
    )

    assert TSchema.model_json_schema() == PSchema.model_json_schema()


def test_nested_json_schema_has_equivalent_contract() -> None:
    expected = PRecord.model_json_schema()
    actual = TRecord.model_json_schema()

    assert actual["type"] == expected["type"]
    assert actual["required"] == expected["required"]
    assert actual["additionalProperties"] == expected["additionalProperties"]
    assert set(actual["properties"]) == set(expected["properties"])
    assert actual["properties"]["label"] == expected["properties"]["label"]
    assert actual["properties"]["count"] == expected["properties"]["count"]
    assert actual["$defs"]["TChild"]["properties"] == expected["$defs"]["PChild"][
        "properties"
    ]
