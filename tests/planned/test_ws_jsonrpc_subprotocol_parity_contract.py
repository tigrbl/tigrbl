from tigrbl_core._spec.binding_spec import WsBindingSpec
from tigrbl_core._spec.path_spec import PathSpec


def test_ws_jsonrpc_subprotocol_parity_contract() -> None:
    ws = WsBindingSpec(proto="ws", path="/rpc", framing="jsonrpc", subprotocols=("jsonrpc",))
    wss = WsBindingSpec(proto="wss", path="/rpc", framing="jsonrpc", subprotocols=("jsonrpc",))

    assert ws.subprotocols == wss.subprotocols == ("jsonrpc",)
    assert PathSpec(path="/rpc", kind="ws-jsonrpc").binding_path(ws) == "/rpc"
    assert PathSpec(path="/rpc", kind="wss-jsonrpc").binding_path(wss) == "/rpc"
