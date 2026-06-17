from __future__ import annotations

import pytest

from tigrbl_core._spec.binding_spec import (
    BindingRegistrySpec,
    BindingSpec,
    HttpJsonRpcBindingSpec,
    HttpStreamBindingSpec,
    HttpRestBindingSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    project_binding_runtime_metadata,
    resolve_rest_nested_prefix,
)
from tigrbl_core.config.constants import (
    TIGRBL_NESTED_PATHS_ATTR,
    __JSONRPC_DEFAULT_ENDPOINT__,
    __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__,
)


def test_binding_registry_register_get_and_values() -> None:
    binding = BindingSpec(
        name="list_items",
        spec=HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"),
    )
    registry = BindingRegistrySpec()

    registry.register(binding)

    assert registry.get("list_items") == binding
    assert registry.values() == (binding,)


def test_resolve_rest_nested_prefix_prefers_callable_attr() -> None:
    class Model:
        _nested_path = "/fallback"

        @staticmethod
        def nested_path() -> str:
            return "/callable"

    setattr(Model, TIGRBL_NESTED_PATHS_ATTR, Model.nested_path)

    assert resolve_rest_nested_prefix(Model) == "/callable"


def test_streaming_binding_specs_expose_exchange_and_framing_defaults() -> None:
    stream = HttpStreamBindingSpec(proto="http.stream", path="/events")
    sse = SseBindingSpec(path="/events")
    ws = WsBindingSpec(proto="ws", path="/socket", framing="jsonrpc")
    wt = WebTransportBindingSpec(path="/transport")

    assert stream.exchange == "server_stream"
    assert stream.framing == "stream"
    assert sse.exchange == "server_stream"
    assert sse.framing == "sse"
    assert ws.exchange == "bidirectional_stream"
    assert ws.framing == "jsonrpc"
    assert wt.exchange == "bidirectional_stream"
    assert wt.framing == "webtransport"


def test_jsonrpc_binding_spec_exposes_endpoint_default_from_core_constants() -> None:
    binding = HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Widget.create")

    assert binding.endpoint == __JSONRPC_DEFAULT_ENDPOINT__
    assert __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__[binding.endpoint] == "/rpc"


def test_http_stream_binding_accepts_explicit_client_stream_request_body() -> None:
    binding = HttpStreamBindingSpec(
        proto="http.stream",
        path="/upload",
        methods=("POST",),
        exchange="client_stream",
        framing="ndjson",
    )

    metadata = project_binding_runtime_metadata(binding)

    assert binding.exchange == "client_stream"
    assert metadata["family"] == "stream"
    assert metadata["carrier_kind"] == "http_request_body"
    assert metadata["stream_initiator"] == "client"
    assert metadata["direction"] == "client_to_server"


def test_http_stream_binding_rejects_native_bidirectional_exchange() -> None:
    with pytest.raises(ValueError, match="unsupported exchange"):
        HttpStreamBindingSpec(
            proto="http.stream",
            path="/duplex",
            exchange="bidirectional_stream",
        )
