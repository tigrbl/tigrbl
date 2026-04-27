from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_dispatch_atoms_derive_rest_jsonrpc_stream_sse_and_ws_metadata() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    cases = (
        (
            {"binding": "http.rest", "method": "GET", "path": "/items"},
            {
                "exchange": "request_response",
                "family": "request_response",
                "subevent": "request.received",
            },
        ),
        (
            {"binding": "http.jsonrpc", "method": "items.list"},
            {"exchange": "request_response", "family": "rpc", "subevent": "rpc.request"},
        ),
        (
            {"binding": "http.stream", "path": "/items/stream"},
            {"exchange": "server_stream", "family": "stream", "subevent": "stream.start"},
        ),
        (
            {"binding": "http.sse", "path": "/items/events"},
            {"exchange": "server_stream", "family": "event_stream", "subevent": "message.emit"},
        ),
        (
            {"binding": "websocket", "path": "/socket"},
            {
                "exchange": "bidirectional_stream",
                "family": "socket",
                "subevent": "message.received",
            },
        ),
    )

    for event, expected in cases:
        metadata = derive(event)
        for key, value in expected.items():
            assert metadata[key] == value


def test_dispatch_atoms_fail_closed_before_handler_on_unknown_binding() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    with pytest.raises(ValueError, match="binding|exchange|subevent|unsupported"):
        derive({"binding": "unknown.transport", "path": "/items"})


def test_dispatch_atoms_run_before_operation_resolution() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")
    resolve = _require("tigrbl_runtime.protocol.dispatch_atoms", "resolve_operation")

    metadata = derive({"binding": "http.rest", "method": "POST", "path": "/items"})
    operation = resolve(metadata)

    assert operation["exchange"] == "request_response"
    assert operation["family"] == "request_response"
    assert operation["subevent"] == "request.received"
    assert operation["op_code"]

