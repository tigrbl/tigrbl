from __future__ import annotations

from typing import Literal
from uuid import UUID

from tigrbl_model import ConfigDict, Field, Model, RootModel


class Child(Model):
    id: UUID


class Parent(Model):
    model_config = ConfigDict(
        extra="forbid", json_schema_extra={"examples": [{"name": "demo"}]}
    )
    name: str = Field(min_length=2, examples=["demo"])
    child: Child
    state: Literal["open", "closed"] = "open"


def test_object_schema_contains_required_defaults_constraints_and_defs() -> None:
    schema = Parent.model_json_schema()

    assert schema["type"] == "object"
    assert schema["required"] == ["name", "child"]
    assert schema["additionalProperties"] is False
    assert schema["properties"]["name"]["minLength"] == 2
    assert schema["properties"]["state"]["default"] == "open"
    assert schema["properties"]["child"] == {"$ref": "#/$defs/Child"}
    assert schema["$defs"]["Child"]["properties"]["id"]["format"] == "uuid"
    assert schema["examples"] == [{"name": "demo"}]


def test_custom_reference_template_is_honored() -> None:
    schema = Parent.model_json_schema(ref_template="#/components/schemas/{model}")
    assert schema["properties"]["child"] == {
        "$ref": "#/components/schemas/Child"
    }


def test_root_model_schema_projects_root_type() -> None:
    Values = RootModel[list[int]]
    schema = Values.model_json_schema()
    assert schema["type"] == "array"
    assert schema["items"] == {"type": "integer"}


def test_callable_json_schema_extra_can_mutate_field_schema() -> None:
    def add_examples(schema):
        schema["examples"] = ["example"]

    class Document(Model):
        value: str = Field(json_schema_extra=add_examples)

    assert Document.model_json_schema()["properties"]["value"]["examples"] == [
        "example"
    ]
