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


def test_framing_decode_atom_handles_json_and_jsonrpc_payloads() -> None:
    decode = _require("tigrbl_runtime.protocol.framing_atoms", "decode_frame")

    json_payload = decode("json", b'{"name":"Ada"}')
    rpc_payload = decode(
        "jsonrpc",
        b'{"jsonrpc":"2.0","id":7,"method":"items.create","params":{"name":"Ada"}}',
    )

    assert json_payload["name"] == "Ada"
    assert rpc_payload["jsonrpc"] == "2.0"
    assert rpc_payload["method"] == "items.create"
    assert rpc_payload["params"]["name"] == "Ada"


def test_framing_encode_atom_handles_jsonrpc_sse_and_websocket_payloads() -> None:
    encode = _require("tigrbl_runtime.protocol.framing_atoms", "encode_frame")

    rpc = encode("jsonrpc", {"id": 7, "result": {"ok": True}})
    sse = encode("sse", {"event": "item", "id": "1", "retry": 1000, "data": "ready"})
    ws = encode("websocket.text", {"text": "ready"})

    assert b'"jsonrpc":"2.0"' in rpc or b'"jsonrpc": "2.0"' in rpc
    assert b"event: item" in sse
    assert b"id: 1" in sse
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

