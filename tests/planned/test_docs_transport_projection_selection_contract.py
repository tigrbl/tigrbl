from tigrbl_core._spec.binding_spec import WsBindingSpec
from tigrbl_core._spec.docs_spec import DocsProjectionSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_core._spec.path_spec import PathSpec


def test_docs_transport_projection_selection_contract() -> None:
    op = OpSpec(
        alias="socket_rpc",
        target="custom",
        bindings=(
            WsBindingSpec(
                proto="wss",
                path="/rpc",
                framing="jsonrpc",
                subprotocols=("jsonrpc",),
            ),
        ),
    )
    path = PathSpec(path="/rpc", kind="wss-jsonrpc", ops=(op,))

    projection = DocsProjectionSpec(
        name="websocket-jsonrpc",
        include_protocols=("wss",),
        include_framings=("jsonrpc",),
        include_subprotocols=("jsonrpc",),
    )

    selected = projection.select((path,))

    assert len(selected) == 1
    assert selected[0].path == "/rpc"
    assert selected[0].protocols == ("wss",)
    assert selected[0].framings == ("jsonrpc",)
