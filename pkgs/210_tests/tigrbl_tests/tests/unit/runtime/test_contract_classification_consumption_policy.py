from __future__ import annotations

import pytest

from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


def test_contract_to_kernelplan_alias_matrix_accepts_canonical_http_profiles() -> None:
    rows = (
        (
            {"kind": "http", "profile": "rest", "path": "/items", "framing": "json"},
            ("http.rest", "request", "json"),
        ),
        (
            {"kind": "http", "profile": "jsonrpc", "rpc_method": "Item.read", "framing": "jsonrpc"},
            ("http.jsonrpc", "request", "jsonrpc"),
        ),
        (
            {"kind": "https", "profile": "stream", "path": "/stream", "framing": "ndjson"},
            ("https.stream", "stream", "ndjson"),
        ),
        (
            {"kind": "https", "profile": "sse", "path": "/events", "framing": "sse"},
            ("https.sse", "stream", "sse"),
        ),
    )

    for binding, expected in rows:
        plan = compile_binding_protocol_plan("Item.read", binding)
        assert (plan["binding_kind"], plan["family"], plan["framing"]) == expected
        assert "subsurface" not in plan


def test_contract_to_kernelplan_alias_matrix_accepts_websocket_profiles() -> None:
    plan = compile_binding_protocol_plan(
        "Socket.echo",
        {
            "kind": "websocket",
            "proto": "wss",
            "profile": "websocket",
            "path": "/socket",
            "framing": "jsonrpc",
            "subprotocols": ("jsonrpc",),
        },
    )

    assert plan["binding_kind"] == "wss"
    assert plan["family"] == "message"
    assert plan["framing"] == "jsonrpc"

    ndjson_plan = compile_binding_protocol_plan(
        "Socket.events",
        {
            "kind": "websocket",
            "proto": "ws",
            "profile": "websocket",
            "path": "/socket/events",
            "framing": "ndjson",
            "subprotocols": ("ndjson",),
        },
    )

    assert ndjson_plan["binding_kind"] == "ws"
    assert ndjson_plan["family"] == "message"
    assert ndjson_plan["framing"] == "ndjson"


def test_kernelplan_rejects_unsupported_framing_combinations_before_runtime() -> None:
    invalid = (
        {"kind": "http", "profile": "rest", "path": "/items", "framing": "jsonrpc"},
        {"kind": "http", "profile": "jsonrpc", "rpc_method": "Item.read", "framing": "json"},
        {"kind": "http", "profile": "sse", "path": "/events", "framing": "json"},
        {"kind": "webtransport", "path": "/transport", "framing": "jsonrpc"},
    )

    for binding in invalid:
        with pytest.raises(ValueError, match="framing|subprotocols|unsupported"):
            compile_binding_protocol_plan("Bad.binding", binding)


def test_contract_classification_consumption_preserves_canonical_event_names() -> None:
    plan = compile_binding_protocol_plan(
        "Item.events",
        {"kind": "http", "profile": "sse", "path": "/events", "framing": "sse"},
    )

    subevents = {row["subevent"] for row in plan["lifecycle_rows"]}
    assert {"message.encoded", "message.emit", "stream.close"} <= subevents
    assert all("subsurface" not in row for row in plan["lifecycle_rows"])
