"""Executable contracts reproducing the Pydantic patterns used by Tigrbl."""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID, uuid4

import pytest

from tigrbl_model import (
    AliasChoices,
    ConfigDict,
    Field,
    Model,
    RootModel,
    ValidationError,
    create_model,
    model_validator,
)


def test_dynamic_crud_schema_pattern() -> None:
    fields = {
        "name": (
            str,
            Field(
                ...,
                validation_alias=AliasChoices("name", "display_name"),
                serialization_alias="displayName",
                min_length=1,
                max_length=80,
                description="Display name",
                json_schema_extra={"examples": ["widget"]},
            ),
        ),
        "quantity": (int | None, Field(default=None, ge=0)),
    }
    Input = create_model(
        "WidgetCreate",
        __config__=ConfigDict(extra="forbid", from_attributes=True),
        **fields,
    )
    Input.model_rebuild(force=True)

    value = Input.model_validate({"display_name": "bolt", "quantity": "2"})
    assert value.model_dump(by_alias=True) == {
        "displayName": "bolt",
        "quantity": 2,
    }
    schema = Input.model_json_schema()
    assert schema["properties"]["name"]["description"] == "Display name"
    assert schema["properties"]["name"]["examples"] == ["widget"]
    serialization_schema = Input.model_json_schema(mode="serialization")
    assert "displayName" in serialization_schema["properties"]
    with pytest.raises(ValidationError):
        Input.model_validate({"name": "bolt", "unknown": True})


def test_from_attributes_pattern() -> None:
    class Row:
        id = 7
        name = "widget"

    class Output(Model):
        model_config = ConfigDict(from_attributes=True)
        id: int
        name: str

    assert Output.model_validate(Row()).model_dump() == {"id": 7, "name": "widget"}


def test_bulk_root_model_pattern() -> None:
    Item = create_model("Item", id=(int, ...))
    BulkRequest = RootModel[list[Item]]
    BulkRequest.__name__ = "WidgetBulkCreateRequest"
    BulkRequest.model_rebuild(force=True)

    value = BulkRequest.model_validate([{"id": "1"}, {"id": 2}])
    assert value.model_dump() == [{"id": 1}, {"id": 2}]
    assert BulkRequest.model_json_schema()["title"] == "WidgetBulkCreateRequest"


def _uuid_examples(schema: dict[str, Any]) -> None:
    schema["examples"] = [str(UUID(int=0))]


class JSONRPCRequest(Model):
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: dict[str, Any] | list[Any] = Field(default_factory=dict)
    id: UUID | str | int | None = Field(
        default_factory=uuid4,
        json_schema_extra=_uuid_examples,
    )


class JSONRPCResponse(Model):
    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: dict[str, Any] | None = None
    id: UUID | str | int | None = None

    @model_validator(mode="after")
    def result_or_error(self):
        if (self.result is None) == (self.error is None):
            raise ValueError("JSON-RPC response requires exactly one of result or error")
        return self


def test_jsonrpc_envelope_pattern() -> None:
    request = JSONRPCRequest(method="widgets.list")
    assert request.jsonrpc == "2.0"
    assert request.params == {}
    assert isinstance(request.id, UUID)
    assert JSONRPCRequest.model_json_schema()["properties"]["id"]["examples"]

    assert JSONRPCResponse(result={"ok": True}).model_dump(exclude_none=True) == {
        "jsonrpc": "2.0",
        "result": {"ok": True},
    }
    with pytest.raises(ValidationError, match="exactly one"):
        JSONRPCResponse()


def test_client_json_encoding_pattern() -> None:
    request = JSONRPCRequest(method="widgets.read", params={"id": 1})
    encoded = request.model_dump_json(exclude_none=True, exclude=None)
    assert JSONRPCRequest.model_validate_json(encoded) == request


def test_openrpc_reference_template_pattern() -> None:
    class Envelope(Model):
        request: JSONRPCRequest

    schema = Envelope.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )
    assert schema["properties"]["request"] == {
        "$ref": "#/components/schemas/JSONRPCRequest"
    }
