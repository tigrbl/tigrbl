import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_wsbindingspec_framing_subprotocol_validation_contract() -> None:
    with pytest.raises(ValueError, match="jsonrpc|subprotocols"):
        WsBindingSpec(proto="ws", path="/rpc", framing="jsonrpc")

    spec = WsBindingSpec(
        proto="wss",
        path="/rpc",
        framing="jsonrpc",
        subprotocols=("jsonrpc",),
    )
    assert spec.proto == "wss"
