from tigrbl_core._spec.binding_spec import (
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.path_spec import PathSpec


def test_transport_scenario_matrix_contract() -> None:
    scenarios = (
        (
            PathSpec(path="/items", kind="resource"),
            HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"),
        ),
        (
            PathSpec(path="/rpc", kind="jsonrpc"),
            HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="items.list", endpoint="/rpc"),
        ),
        (
            PathSpec(path="/stream", kind="stream"),
            HttpStreamBindingSpec(proto="http.stream", path="/stream"),
        ),
        (PathSpec(path="/events", kind="sse"), SseBindingSpec(path="/events")),
        (PathSpec(path="/socket", kind="websocket"), WsBindingSpec(proto="ws", path="/socket")),
        (
            PathSpec(path="/transport", kind="webtransport"),
            WebTransportBindingSpec(path="/transport"),
        ),
    )

    for path, binding in scenarios:
        path.validate_binding_convergence(binding)
