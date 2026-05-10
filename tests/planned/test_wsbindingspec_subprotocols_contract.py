from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_wsbindingspec_subprotocols_contract() -> None:
    spec = WsBindingSpec(
        proto="wss",
        path="/rpc",
        framing="jsonrpc",
        subprotocols=("JSONRPC", "TIGRBL"),
    )

    assert spec.subprotocols == ("jsonrpc", "tigrbl")
    assert spec.exchange == "bidirectional_stream"
