from tigrbl_concrete.system.docs.surface import binding_surface
from tigrbl_core._spec.binding_spec import WsBindingSpec


def test_docs_websocket_transport_projection_contract() -> None:
    binding = WsBindingSpec(
        proto="wss",
        path="/rpc",
        framing="jsonrpc",
        subprotocols=("jsonrpc",),
    )

    surface = binding_surface(binding)

    assert surface["proto"] == "wss"
    assert surface["path"] == "/rpc"
    assert surface["framing"] == "jsonrpc"
    assert surface["subprotocols"] == ("jsonrpc",)
    assert surface["family"] == "socket"
