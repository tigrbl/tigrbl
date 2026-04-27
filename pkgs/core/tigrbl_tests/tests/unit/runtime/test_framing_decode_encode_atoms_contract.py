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


def test_framing_decode_atom_handles_json_payload() -> None:
    decode = _require("tigrbl_runtime.protocol.framing_atoms", "decode_frame")

    json_payload = decode("json", b'{"name":"Ada"}')

    assert json_payload["name"] == "Ada"


def test_framing_decode_atom_handles_jsonrpc_payload() -> None:
    decode = _require("tigrbl_runtime.protocol.framing_atoms", "decode_frame")

    rpc_payload = decode(
        "jsonrpc",
        b'{"jsonrpc":"2.0","id":7,"method":"items.create","params":{"name":"Ada"}}',
    )

    assert rpc_payload["jsonrpc"] == "2.0"
    assert rpc_payload["id"] == 7
    assert rpc_payload["method"] == "items.create"
    assert rpc_payload["params"]["name"] == "Ada"


def test_framing_encode_atom_handles_jsonrpc_success_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.framing_atoms", "encode_frame")

    rpc = encode("jsonrpc", {"id": 7, "result": {"ok": True}})

    assert b'"jsonrpc":"2.0"' in rpc or b'"jsonrpc": "2.0"' in rpc
    assert b'"id":7' in rpc or b'"id": 7' in rpc
    assert b'"result"' in rpc


def test_framing_encode_atom_handles_jsonrpc_error_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.framing_atoms", "encode_frame")

    rpc = encode("jsonrpc", {"id": 7, "error": {"code": -32600, "message": "Invalid Request"}})

    assert b'"jsonrpc":"2.0"' in rpc or b'"jsonrpc": "2.0"' in rpc
    assert b'"id":7' in rpc or b'"id": 7' in rpc
    assert b'"error"' in rpc
    assert b"-32600" in rpc


def test_framing_encode_atom_handles_sse_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.framing_atoms", "encode_frame")

    sse = encode("sse", {"event": "item", "id": "1", "retry": 1000, "data": "ready"})

    assert b"event: item" in sse
    assert b"id: 1" in sse
    assert b"retry: 1000" in sse
    assert b"data: ready" in sse


def test_framing_encode_atom_handles_websocket_text_payload() -> None:
    encode = _require("tigrbl_runtime.protocol.framing_atoms", "encode_frame")

    ws = encode("websocket.text", {"text": "ready"})

    assert ws == {"type": "websocket.send", "text": "ready"}


@pytest.mark.parametrize(
    ("framing", "payload"),
    (
        ("json", b"{bad-json"),
        ("jsonrpc", b'{"jsonrpc":"2.0","params":[]}'),
        ("websocket.text", b"\xff"),
    ),
)
def test_framing_decode_atom_maps_malformed_payloads_to_typed_errors(
    framing: str, payload: bytes
) -> None:
    decode = _require("tigrbl_runtime.protocol.framing_atoms", "decode_frame")

    with pytest.raises(ValueError, match="framing|decode|invalid|malformed"):
        decode(framing, payload)
