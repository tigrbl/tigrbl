from decimal import Decimal
from typing import Any

from jsonschema import validate
from pydantic import BaseModel

from tigrbl_core._spec import OpSpec
from tigrbl_core.schema import build_operation_result_json_schema


class Row(BaseModel):
    name: str
    amount: Decimal | None = None


def custom_cards(_cls: type, _ctx: dict[str, Any]) -> list[dict[str, Any]]:
    return []


def custom_dashboard(_cls: type, _ctx: dict[str, Any]) -> dict[str, Any]:
    return {}


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
