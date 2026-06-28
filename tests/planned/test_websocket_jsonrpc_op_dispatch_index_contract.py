import pytest


pytestmark = pytest.mark.xfail(
    reason="planned WebSocket JSON-RPC dispatch index contract; implementation scope not frozen",
    strict=False,
)


def test_websocket_jsonrpc_path_op_index_contract() -> None:
    assert False


def test_websocket_jsonrpc_duplicate_method_rejection_contract() -> None:
    assert False


def test_websocket_jsonrpc_shared_http_dispatcher_parity() -> None:
    assert False
