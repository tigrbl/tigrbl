import pytest

from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_wsbindingspec_framing_contract() -> None:
    assert WsBindingSpec(proto="ws", path="/socket").framing == "text"
    assert (
        WsBindingSpec(
            proto="ws",
            path="/rpc",
            framing="jsonrpc",
            subprotocols=("jsonrpc",),
        ).framing
        == "jsonrpc"
    )

    with pytest.raises(ValueError, match="jsonld|fail closed|planned"):
        WsBindingSpec(proto="ws", path="/jsonld", framing="jsonld")
