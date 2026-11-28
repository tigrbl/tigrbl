from decimal import Decimal
from typing import Any

from jsonschema import validate
from pydantic import BaseModel, RootModel

from tigrbl_core._spec import OpSpec
from tigrbl_core.schema import build_operation_result_json_schema


class Row(BaseModel):
    name: str
    amount: Decimal | None = None


class ExplicitResult(BaseModel):
    accepted: bool


class RowCollection(RootModel[list[Row]]):
    pass


def custom_cards(_cls: type, _ctx: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def custom_dashboard(_cls: type, _ctx: dict[str, Any]) -> dict[str, Any]:
    return {}


def custom_scalar(_cls: type, _ctx: dict[str, Any]) -> str | None:
    return None


def custom_mismatched_annotation(
    _cls: type, _ctx: dict[str, Any]
) -> list[dict[str, Any]]:
    return []


def test_list_result_schema_wraps_the_element_model() -> None:
    schema = build_operation_result_json_schema(
        OpSpec(alias="list", target="list"),
        Row,
    )

    assert schema["type"] == "array"
    validate([{"name": "first", "amount": "0E-10"}], schema)


def test_custom_result_schema_follows_the_handler_return_annotation() -> None:
    cards = build_operation_result_json_schema(
        OpSpec(alias="cards", target="custom"),
        Row,
        handler=custom_cards,
    )
    dashboard = build_operation_result_json_schema(
        OpSpec(alias="dashboard", target="custom"),
        Row,
        handler=custom_dashboard,
    )

    assert cards["type"] == "array"
    assert dashboard["type"] == "object"
    validate([{"id": "card-one"}], cards)
    validate({"summary": {"count": 1}}, dashboard)


def test_explicit_response_model_precedes_custom_handler_annotation() -> None:
    schema = build_operation_result_json_schema(
        OpSpec(
            alias="decision",
            target="custom",
            response_model=ExplicitResult,
        ),
        ExplicitResult,
        handler=custom_mismatched_annotation,
    )

    assert schema["type"] == "object"
    assert set(schema["properties"]) == {"accepted"}
    validate({"accepted": True}, schema)


def test_custom_scalar_union_uses_handler_return_annotation() -> None:
    schema = build_operation_result_json_schema(
        OpSpec(alias="label", target="custom"),
        Row,
        handler=custom_scalar,
    )

    assert {branch["type"] for branch in schema["anyOf"]} == {"string", "null"}
    validate("ready", schema)
    validate(None, schema)


def test_list_root_model_is_not_wrapped_twice() -> None:
    schema = build_operation_result_json_schema(
        OpSpec(alias="list", target="list"),
        RowCollection,
    )

    assert schema["type"] == "array"
    assert schema["items"]["$ref"].endswith("/Row")
    validate([{"name": "first", "amount": None}], schema)


def test_unannotated_custom_handler_falls_back_to_bound_output_model() -> None:
    def unannotated(_cls, _ctx):
        return {}

    schema = build_operation_result_json_schema(
        OpSpec(alias="fallback", target="custom"),
        Row,
        handler=unannotated,
    )

    assert schema["type"] == "object"
    assert "name" in schema["properties"]
