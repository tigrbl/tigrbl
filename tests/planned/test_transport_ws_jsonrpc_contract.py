from tigrbl_core._spec.binding_spec import WsBindingSpec, project_binding_runtime_metadata
from tigrbl_core._spec.path_spec import PathSpec


def test_transport_ws_jsonrpc_contract() -> None:
    binding = WsBindingSpec(
        proto="ws",
        path="/rpc",
        framing="jsonrpc",
        subprotocols=("jsonrpc",),
    )
    path = PathSpec(path="/rpc", kind="ws-jsonrpc")

    assert path.binding_path(binding) == "/rpc"
    assert project_binding_runtime_metadata(binding)["family"] == "socket"
