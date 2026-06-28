import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket JSON-RPC framing codec atom contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_jsonrpc_framing_decode_atom_contract() -> None:
    assert False


def test_websocket_jsonrpc_framing_encode_atom_contract() -> None:
    assert False


def test_websocket_jsonrpc_inferred_subprotocol_contract() -> None:
    assert False
