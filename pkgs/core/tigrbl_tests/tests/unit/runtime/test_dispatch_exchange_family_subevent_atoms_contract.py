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


def test_dispatch_atom_derives_rest_request_metadata() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    metadata = derive({"binding": "http.rest", "method": "GET", "path": "/items"})

    assert metadata["exchange"] == "request_response"
    assert metadata["family"] == "request_response"
    assert metadata["subevent"] == "request.received"


def test_dispatch_atom_derives_jsonrpc_request_metadata() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    metadata = derive({"binding": "http.jsonrpc", "method": "items.list"})

    assert metadata["exchange"] == "request_response"
    assert metadata["family"] == "rpc"
    assert metadata["subevent"] == "rpc.request"


@pytest.mark.parametrize(
    ("event", "expected"),
    (
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
    ),
)
def test_dispatch_atom_derives_eventful_transport_metadata(event, expected) -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    metadata = derive(event)

    assert {key: metadata[key] for key in expected} == expected


def test_dispatch_atoms_fail_closed_before_handler_on_unknown_binding() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    with pytest.raises(ValueError, match="binding|exchange|subevent|unsupported"):
        derive({"binding": "unknown.transport", "path": "/items"})


def test_dispatch_metadata_feeds_operation_resolution() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")
    resolve = _require("tigrbl_runtime.protocol.dispatch_atoms", "resolve_operation")

    metadata = derive({"binding": "http.rest", "method": "POST", "path": "/items"})
    operation = resolve(metadata)

    assert operation["exchange"] == "request_response"
    assert operation["family"] == "request_response"
    assert operation["subevent"] == "request.received"
    assert operation["op_code"]


def test_dispatch_atom_rejects_unqualified_subevent_aliases() -> None:
    derive = _require("tigrbl_runtime.protocol.dispatch_atoms", "derive_runtime_event")

    with pytest.raises(ValueError, match="qualified|subevent|request.received"):
        derive({"binding": "http.rest", "method": "GET", "subevent": "receive"})
