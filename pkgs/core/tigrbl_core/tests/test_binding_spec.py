from __future__ import annotations

from tigrbl_core._spec.binding_spec import (
    BindingRegistrySpec,
    BindingSpec,
    HttpStreamBindingSpec,
    HttpRestBindingSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    resolve_rest_nested_prefix,
)
from tigrbl_core.config.constants import TIGRBL_NESTED_PATHS_ATTR


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
    assert ws.exchange == "bidirectional"
    assert ws.framing == "jsonrpc"
    assert wt.exchange == "bidirectional"
    assert wt.framing == "webtransport"
