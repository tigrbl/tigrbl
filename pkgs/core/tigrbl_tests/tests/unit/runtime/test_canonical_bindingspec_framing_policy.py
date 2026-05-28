from __future__ import annotations

import pytest

import tigrbl
from tigrbl import (
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
)


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


def test_websocket_jsonrpc_and_ndjson_fail_closed_policy() -> None:
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
    with pytest.raises(ValueError, match="framing"):
        WsBindingSpec(proto="wss", path="/socket", framing="ndjson")


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

