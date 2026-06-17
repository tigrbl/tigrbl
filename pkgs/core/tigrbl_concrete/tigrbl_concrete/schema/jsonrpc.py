from __future__ import annotations

from typing import Any, Literal, TypeAlias
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator


JSONRPCId: TypeAlias = UUID | str | int | None
JSONRPCParams: TypeAlias = dict[str, Any] | list[Any]


def _uuid_examples(schema: dict[str, Any]) -> None:
    schema["examples"] = [str(uuid4())]


class JSONRPCRequest(BaseModel):
    """JSON-RPC 2.0 request envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: JSONRPCParams = Field(default_factory=dict)
    id: JSONRPCId = Field(default_factory=uuid4, json_schema_extra=_uuid_examples)


class JSONRPCNotification(BaseModel):
    """JSON-RPC 2.0 notification envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: JSONRPCParams = Field(default_factory=dict)


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Any | None = None


class JSONRPCSuccessResponse(BaseModel):
    """JSON-RPC 2.0 success response envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    result: Any
    id: JSONRPCId = Field(default=None, json_schema_extra=_uuid_examples)


class JSONRPCErrorResponse(BaseModel):
    """JSON-RPC 2.0 error response envelope."""

    jsonrpc: Literal["2.0"] = "2.0"
    error: JSONRPCError
    id: JSONRPCId = Field(default=None, json_schema_extra=_uuid_examples)


class JSONRPCResponse(BaseModel):
    """Compatibility response envelope with JSON-RPC result/error one-of rules."""

    jsonrpc: Literal["2.0"] = "2.0"
    result: Any | None = None
    error: JSONRPCError | None = None
    id: JSONRPCId = Field(default=None, json_schema_extra=_uuid_examples)

    @model_validator(mode="after")
    def _result_or_error(self) -> "JSONRPCResponse":
        has_result = self.result is not None
        has_error = self.error is not None
        if has_result == has_error:
            raise ValueError("JSON-RPC response requires exactly one of result or error")
        return self


class JSONRPCBatch(BaseModel):
    """JSON-RPC 2.0 non-empty batch envelope."""

    messages: list[
        JSONRPCRequest
        | JSONRPCNotification
        | JSONRPCSuccessResponse
        | JSONRPCErrorResponse
    ]

    @model_validator(mode="after")
    def _non_empty(self) -> "JSONRPCBatch":
        if not self.messages:
            raise ValueError("JSON-RPC batch must not be empty")
        return self


RPCRequest = JSONRPCRequest
RPCError = JSONRPCError
RPCResponse = JSONRPCResponse


__all__ = [
    "JSONRPCBatch",
    "JSONRPCError",
    "JSONRPCErrorResponse",
    "JSONRPCId",
    "JSONRPCNotification",
    "JSONRPCParams",
    "JSONRPCRequest",
    "JSONRPCResponse",
    "JSONRPCSuccessResponse",
    "RPCError",
    "RPCRequest",
    "RPCResponse",
]
