from __future__ import annotations

import pytest

from tigrbl_core._spec import (
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
        framing="jsonrpc",
        subprotocols=("JSONRPC", "V2"),
    )

    assert binding.subprotocols == ("jsonrpc", "v2")
    assert binding.framing == "jsonrpc"
    assert project_binding_runtime_metadata(binding) == {
        "proto": "wss",
        "exchange": "bidirectional_stream",
        "framing": "jsonrpc",
        "family": "message",
        "subevents": ("message.received", "message.processed"),
    }


def test_wsbindingspec_jsonrpc_implicit_subprotocol_is_stable() -> None:
    binding = WsBindingSpec(proto="ws", path="/rpc", framing="jsonrpc")

    assert binding.subprotocols == ("jsonrpc",)


@pytest.mark.parametrize("proto", ("ws", "wss"))
def test_websocket_jsonrpc_framing_requires_jsonrpc_subprotocol(proto: str) -> None:
    with pytest.raises(ValueError, match="requires subprotocols"):
        WsBindingSpec(
            proto=proto,  # type: ignore[arg-type]
            path="/rpc",
            framing="jsonrpc",
            subprotocols=("graphql-ws",),
        )


@pytest.mark.parametrize("proto", ("ws", "wss"))
def test_websocket_ndjson_requires_matching_subprotocol(proto: str) -> None:
    with pytest.raises(ValueError, match="requires subprotocols"):
        WsBindingSpec(
            proto=proto,  # type: ignore[arg-type]
            path="/stream",
            framing="ndjson",
        )

    binding = WsBindingSpec(
        proto=proto,  # type: ignore[arg-type]
        path="/stream",
        framing="ndjson",
        subprotocols=("NDJSON",),
    )

    assert binding.framing == "ndjson"
    assert binding.subprotocols == ("ndjson",)


@pytest.mark.parametrize("framing", ("sse", "webtransport", "stream"))
def test_websocket_unsupported_framing_values_fail_closed(framing: str) -> None:
    with pytest.raises(ValueError, match="unsupported app-level framing"):
        validate_app_framing_for_binding(binding_kind="ws", framing=framing)


def test_websocket_binding_alias_normalizes_without_losing_subprotocols() -> None:
    binding = WsBindingSpec(
        proto="ws",
        path="/rpc",
        framing="jsonrpc",
        subprotocols=("JSONRPC",),
    )

    normalized = normalize_binding_spec(binding)

    assert isinstance(normalized, WebSocketBindingSpec)
    assert normalized.proto == "ws"
    assert normalized.framing == "jsonrpc"
    assert normalized.subprotocols == ("jsonrpc",)


def test_websocket_runtime_metadata_rejects_invalid_exchange_before_plan_use() -> None:
    with pytest.raises(ValueError, match="unsupported exchange"):
        WsBindingSpec(
            proto="ws",
            path="/rpc",
            framing="jsonrpc",
            exchange="server_stream",  # type: ignore[arg-type]
        )
