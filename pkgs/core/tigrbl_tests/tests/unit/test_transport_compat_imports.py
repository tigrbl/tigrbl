from __future__ import annotations

import warnings


def test_deprecated_jsonrpc_model_imports_reexport_schema_namespace() -> None:
    from tigrbl.schema.jsonrpc import RPCError, RPCRequest, RPCResponse
    from tigrbl_concrete.schema.jsonrpc import (
        RPCError as ConcreteRPCError,
        RPCRequest as ConcreteRPCRequest,
        RPCResponse as ConcreteRPCResponse,
    )

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from tigrbl.transport.jsonrpc.models import RPCRequest as PublicTransportRequest
        from tigrbl_concrete.transport.jsonrpc.models import (
            RPCRequest as ConcreteTransportRequest,
        )

    assert RPCRequest is ConcreteRPCRequest
    assert RPCResponse is ConcreteRPCResponse
    assert RPCError is ConcreteRPCError
    assert PublicTransportRequest is RPCRequest
    assert ConcreteTransportRequest is RPCRequest


def test_deprecated_jsonrpc_helpers_remain_importable() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from tigrbl.transport.jsonrpc.helpers import _err, _ok
        from tigrbl_concrete.transport.jsonrpc.helpers import _normalize_params

    assert _ok({"value": 1}, "abc") == {
        "jsonrpc": "2.0",
        "result": {"value": 1},
        "id": "abc",
    }
    assert _err(-32600, "Invalid Request", None)["error"]["code"] == -32600
    assert _normalize_params({"params": {"x": 1}}) == {"x": 1}


def test_deprecated_rest_aggregators_remain_importable() -> None:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from tigrbl.transport.rest.aggregator import build_rest_router
        from tigrbl_concrete.transport.rest.aggregator import mount_rest

    assert callable(build_rest_router)
    assert callable(mount_rest)
