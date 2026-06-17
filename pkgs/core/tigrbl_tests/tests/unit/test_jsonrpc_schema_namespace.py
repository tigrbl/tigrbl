from __future__ import annotations

from pydantic import ValidationError
import pytest


def test_jsonrpc_schema_namespace_exports_public_envelopes() -> None:
    from tigrbl.schema import jsonrpc
    from tigrbl_concrete.schema.jsonrpc import JSONRPCRequest

    assert jsonrpc.JSONRPCRequest is JSONRPCRequest
    assert jsonrpc.RPCRequest is JSONRPCRequest
    assert jsonrpc.JSONRPCNotification(method="items.changed").jsonrpc == "2.0"
    assert jsonrpc.JSONRPCSuccessResponse(id=1, result={"ok": True}).result == {
        "ok": True
    }
    assert jsonrpc.JSONRPCErrorResponse(
        id=1,
        error={"code": -32600, "message": "Invalid Request"},
    ).error.code == -32600
    assert jsonrpc.JSONRPCBatch(
        messages=[
            {"method": "items.list", "id": 1},
            {"method": "items.changed"},
            {"id": 1, "result": []},
        ]
    ).messages


def test_jsonrpc_schema_response_requires_exactly_one_result_or_error() -> None:
    from tigrbl.schema.jsonrpc import JSONRPCResponse

    assert JSONRPCResponse(id=1, result=[]).result == []
    with pytest.raises(ValidationError, match="exactly one"):
        JSONRPCResponse(id=1)
    with pytest.raises(ValidationError, match="exactly one"):
        JSONRPCResponse(
            id=1,
            result=[],
            error={"code": -32600, "message": "Invalid Request"},
        )


def test_rpc_request_id_schema_examples_remain_dynamic() -> None:
    from tigrbl.schema.jsonrpc import RPCRequest

    schema1 = RPCRequest.model_json_schema()
    schema2 = RPCRequest.model_json_schema()

    assert schema1["properties"]["id"]["examples"][0] != schema2["properties"]["id"][
        "examples"
    ][0]
