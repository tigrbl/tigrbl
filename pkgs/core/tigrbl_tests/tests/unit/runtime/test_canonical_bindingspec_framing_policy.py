from __future__ import annotations

import pytest

import tigrbl
from tigrbl import (
    BINDING_PROFILE_EXCHANGE_SUPPORT,
    HTTPBindingSpec,
    HttpJsonRpcBindingSpec,
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WebSocketBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
    canonical_binding_kind,
    normalize_binding_spec,
    validate_app_framing_for_binding,
    validate_binding_profile_exchange,
)
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


def test_canonical_bindingspec_classes_are_public_exports() -> None:
    assert tigrbl.HTTPBindingSpec is HTTPBindingSpec
    assert tigrbl.WebSocketBindingSpec is WebSocketBindingSpec
    assert tigrbl.WebTransportBindingSpec is WebTransportBindingSpec


def test_alias_to_canonical_normalization_table_is_stable() -> None:
    rows = (
        (HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items"), HTTPBindingSpec, "http.rest", "rest"),
        (HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Item.read"), HTTPBindingSpec, "http.jsonrpc", "jsonrpc"),
        (HttpStreamBindingSpec(proto="https.stream", path="/stream"), HTTPBindingSpec, "https.stream", "stream"),
        (SseBindingSpec(proto="https.sse", path="/events"), HTTPBindingSpec, "https.sse", "sse"),
        (WsBindingSpec(proto="wss", path="/socket"), WebSocketBindingSpec, "wss", "websocket"),
        (WebTransportBindingSpec(path="/transport"), WebTransportBindingSpec, "webtransport", "webtransport"),
    )

    for alias, expected_type, expected_kind, expected_profile in rows:
        canonical = normalize_binding_spec(alias)
        assert isinstance(canonical, expected_type)
        assert canonical_binding_kind(canonical) == expected_kind
        assert canonical.profile == expected_profile


def test_profile_and_framing_are_separate_vocabularies() -> None:
    rest = HTTPBindingSpec(proto="http", profile="rest", path="/items", framing="json")
    rpc = HTTPBindingSpec(proto="http", profile="jsonrpc", rpc_method="Item.read", framing="jsonrpc")
    sse = HTTPBindingSpec(proto="https", profile="sse", path="/events", framing="sse")

    assert rest.profile == "rest"
    assert rest.framing == "json"
    assert rpc.profile == "jsonrpc"
    assert rpc.framing == "jsonrpc"
    assert sse.profile == "sse"
    assert sse.framing == "sse"


def test_canonical_bindingspecs_serde_roundtrip() -> None:
    specs = (
        HTTPBindingSpec(proto="http", profile="rest", path="/items", methods=("GET",)),
        HTTPBindingSpec(proto="http", profile="jsonrpc", rpc_method="Item.read"),
        HTTPBindingSpec(proto="https", profile="stream", path="/stream", framing="ndjson"),
        WebSocketBindingSpec(proto="wss", path="/socket", framing="jsonrpc", subprotocols=("jsonrpc",)),
        WebTransportBindingSpec(path="/transport"),
    )

    for spec in specs:
        assert spec.__class__.from_json(spec.to_json()) == spec


def test_http_framing_policy_runtime_gates() -> None:
    assert validate_app_framing_for_binding(binding_kind="http.rest", framing="json") == "json"
    assert validate_app_framing_for_binding(binding_kind="http.jsonrpc", framing="jsonrpc") == "jsonrpc"
    assert validate_app_framing_for_binding(binding_kind="http.stream", framing="ndjson") == "ndjson"
    assert validate_app_framing_for_binding(binding_kind="http.sse", framing="sse") == "sse"

    with pytest.raises(ValueError, match="framing"):
        validate_app_framing_for_binding(binding_kind="http.rest", framing="sse")
    with pytest.raises(ValueError, match="framing"):
        validate_app_framing_for_binding(binding_kind="http.jsonrpc", framing="json")
    with pytest.raises(ValueError, match="framing"):
        validate_app_framing_for_binding(binding_kind="http.sse", framing="json")


def test_profile_exchange_policy_matrix_is_public_and_fail_closed() -> None:
    assert BINDING_PROFILE_EXCHANGE_SUPPORT == {
        "http.rest": ("request_response",),
        "https.rest": ("request_response",),
        "http.jsonrpc": ("request_response",),
        "https.jsonrpc": ("request_response",),
        "http.stream": ("server_stream",),
        "https.stream": ("server_stream",),
        "http.sse": ("server_stream",),
        "https.sse": ("server_stream",),
        "ws": ("bidirectional_stream",),
        "wss": ("bidirectional_stream",),
        "webtransport": ("bidirectional_stream", "client_stream", "server_stream"),
    }

    for binding_kind, allowed in BINDING_PROFILE_EXCHANGE_SUPPORT.items():
        for exchange in allowed:
            assert (
                validate_binding_profile_exchange(
                    binding_kind=binding_kind,
                    exchange=exchange,
                )
                == exchange
            )

    with pytest.raises(ValueError, match="unsupported binding"):
        validate_binding_profile_exchange(binding_kind="ftp", exchange="request_response")


@pytest.mark.parametrize(
    "spec",
    (
        lambda: HTTPBindingSpec(proto="http", profile="rest", exchange="server_stream"),
        lambda: HTTPBindingSpec(proto="http", profile="jsonrpc", rpc_method="Item.read", exchange="client_stream"),
        lambda: HTTPBindingSpec(proto="https", profile="stream", exchange="client_stream"),
        lambda: HTTPBindingSpec(proto="http", profile="sse", exchange="bidirectional_stream"),
        lambda: WebSocketBindingSpec(proto="ws", path="/socket", exchange="fire_and_forget"),
        lambda: WsBindingSpec(proto="wss", path="/socket", exchange="server_stream"),
        lambda: HttpRestBindingSpec(proto="http.rest", methods=("GET",), path="/items", exchange="server_stream"),
        lambda: HttpJsonRpcBindingSpec(proto="http.jsonrpc", rpc_method="Item.read", exchange="server_stream"),
        lambda: HttpStreamBindingSpec(proto="http.stream", path="/stream", exchange="client_stream"),
        lambda: SseBindingSpec(proto="http.sse", path="/events", exchange="client_stream"),
    ),
)
def test_profile_exchange_negative_corpus(spec) -> None:
    with pytest.raises(ValueError, match="exchange"):
        spec()


@pytest.mark.parametrize(
    "binding",
    (
        {"kind": "http.rest", "path": "/items", "exchange": "server_stream"},
        {"kind": "http.jsonrpc", "rpc_method": "Item.read", "exchange": "client_stream"},
        {"kind": "http.stream", "path": "/stream", "exchange": "client_stream"},
        {"kind": "http.sse", "path": "/events", "exchange": "bidirectional_stream"},
        {"kind": "ws", "path": "/socket", "exchange": "fire_and_forget"},
        {"kind": "wss", "path": "/socket", "exchange": "server_stream"},
    ),
)
def test_kernel_plan_rejects_profile_exchange_drift(binding) -> None:
    with pytest.raises(ValueError, match="exchange"):
        compile_binding_protocol_plan("Transport.bad", binding)


def test_websocket_jsonrpc_and_ndjson_subprotocol_policy() -> None:
    assert (
        validate_app_framing_for_binding(
            binding_kind="ws",
            framing="jsonrpc",
            subprotocols=("jsonrpc",),
        )
        == "jsonrpc"
    )
    with pytest.raises(ValueError, match="subprotocols"):
        WebSocketBindingSpec(proto="ws", path="/socket", framing="jsonrpc")
    with pytest.raises(ValueError, match="subprotocols"):
        WsBindingSpec(proto="wss", path="/socket", framing="ndjson")
    assert WsBindingSpec(
        proto="wss",
        path="/socket",
        framing="ndjson",
        subprotocols=("NDJSON",),
    ).subprotocols == ("ndjson",)


@pytest.mark.parametrize(
    "spec",
    (
        lambda: HTTPBindingSpec(proto="http", profile="rest", framing="jsonrpc"),
        lambda: HTTPBindingSpec(proto="http", profile="jsonrpc", rpc_method="Item.read", framing="ndjson"),
        lambda: HTTPBindingSpec(proto="http", profile="sse", framing="json"),
        lambda: WebTransportBindingSpec(framing="jsonrpc"),
    ),
)
def test_profile_framing_confusion_negative_corpus(spec) -> None:
    with pytest.raises(ValueError, match="framing|JSON-RPC|unsupported"):
        spec()
