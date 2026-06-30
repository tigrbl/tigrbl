from __future__ import annotations

import pytest

from tigrbl_core._spec import (
    JsonRpcFramingSpec,
    NdjsonFramingSpec,
    WebSocketBindingSpec,
    WsBindingSpec,
    normalize_binding_spec,
    validate_app_framing_for_binding,
)
from tigrbl_core._spec.binding_spec import project_binding_runtime_metadata


def test_wsbindingspec_lowercases_subprotocols_and_preserves_jsonrpc_framing() -> None:
    binding = WsBindingSpec(
        proto="wss",
        path="/rpc",
        framing=JsonRpcFramingSpec(),
        subprotocols=("JSONRPC", "V2"),
    )

    assert binding.subprotocols == ("jsonrpc", "v2")
    assert binding.framing == JsonRpcFramingSpec()
    assert project_binding_runtime_metadata(binding) == {
        "proto": "wss",
        "exchange": "bidirectional_stream",
        "framing": "jsonrpc",
        "framing_kind": "jsonrpc",
        "framing_spec": "JsonRpcFramingSpec",
        "family": "message",
        "subevents": ("message.received", "message.processed"),
        "required_subprotocol": "jsonrpc",
        "subprotocols": ("jsonrpc", "v2"),
    }


def test_wsbindingspec_jsonrpc_implicit_subprotocol_is_stable() -> None:
    binding = WsBindingSpec(proto="ws", path="/rpc", framing=JsonRpcFramingSpec())

    assert binding.subprotocols == ("jsonrpc",)


@pytest.mark.parametrize("proto", ("ws", "wss"))
def test_websocket_jsonrpc_framing_rejects_conflicting_subprotocol(proto: str) -> None:
    with pytest.raises(ValueError, match="conflicts with subprotocols"):
        WsBindingSpec(
            proto=proto,  # type: ignore[arg-type]
            path="/rpc",
            framing=JsonRpcFramingSpec(),
            subprotocols=("graphql-ws",),
        )


@pytest.mark.parametrize("proto", ("ws", "wss"))
def test_websocket_ndjson_requires_matching_subprotocol(proto: str) -> None:
    binding = WsBindingSpec(
        proto=proto,  # type: ignore[arg-type]
        path="/stream",
        framing=NdjsonFramingSpec(),
    )

    assert binding.framing == NdjsonFramingSpec()
    assert binding.subprotocols == ("ndjson",)


@pytest.mark.parametrize("framing", ("sse", "webtransport", "stream"))
def test_websocket_unsupported_framing_values_fail_closed(framing: str) -> None:
    with pytest.raises((TypeError, ValueError), match="FramingSpec|unsupported app-level framing"):
        validate_app_framing_for_binding(binding_kind="ws", framing=framing)


def test_websocket_binding_alias_normalizes_without_losing_subprotocols() -> None:
    binding = WsBindingSpec(
        proto="ws",
        path="/rpc",
        framing=JsonRpcFramingSpec(),
        subprotocols=("JSONRPC",),
    )

    normalized = normalize_binding_spec(binding)

    assert isinstance(normalized, WebSocketBindingSpec)
    assert normalized.proto == "ws"
    assert normalized.framing == JsonRpcFramingSpec()
    assert normalized.subprotocols == ("jsonrpc",)


def test_websocket_runtime_metadata_rejects_invalid_exchange_before_plan_use() -> None:
    with pytest.raises(ValueError, match="unsupported exchange"):
        WsBindingSpec(
            proto="ws",
            path="/rpc",
            framing=JsonRpcFramingSpec(),
            exchange="server_stream",  # type: ignore[arg-type]
        )
