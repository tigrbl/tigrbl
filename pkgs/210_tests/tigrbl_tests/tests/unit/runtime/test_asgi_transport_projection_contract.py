from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.transport.asgi_channel import message_payload, payload_size
from tigrbl_kernel.channel_taxonomy import (
    channel_family,
    channel_kind,
    channel_subevents,
    webtransport_event_metadata,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload
from tigrbl_runtime.channel._asgi_scope import build_asgi_channel


def test_websocket_receive_projects_message_received() -> None:
    env = SimpleNamespace(scope={"type": "websocket", "path": "/ws"})
    channel = build_asgi_channel(env, exchange="bidirectional")

    assert channel.kind == "websocket"
    assert channel.family == "socket"
    assert channel.exchange == "bidirectional_stream"
    assert channel.subevents == ("connect", "receive", "emit", "complete", "disconnect")
    assert message_payload({"type": "websocket.receive", "text": "hello"}) == b"hello"


def test_wt_stream_receive_projects_stream_chunk_received() -> None:
    metadata = webtransport_event_metadata(
        direction="receive",
        message={
            "type": "webtransport.stream.receive",
            "session_id": "s1",
            "stream_id": "st1",
            "stream_direction": "bidi",
            "data": b"chunk",
        },
    )

    assert metadata["subevent"] == "stream.chunk.received"
    assert metadata["family"] == "stream"
    assert metadata["lane"] == "bidi_stream"
    assert metadata["exchange"] == "bidirectional_stream"
    assert metadata["stream_initiator"] == "client"
    assert metadata["direction"] == "bidirectional"
    assert payload_size({"data": b"chunk"}) == 5


def test_http_body_stream_projects_by_binding_kind() -> None:
    unary = build_asgi_channel(
        SimpleNamespace(
            scope={
                "type": "http",
                "method": "POST",
                "path": "/items",
                "query_string": b"a=1",
                "headers": [(b"content-type", b"application/json")],
            }
        ),
        exchange="request_response",
    )
    stream = build_asgi_channel(
        SimpleNamespace(scope={"type": "http", "method": "GET", "path": "/events"}),
        exchange="server_stream",
    )
    upload = build_asgi_channel(
        SimpleNamespace(scope={"type": "http", "method": "POST", "path": "/upload"}),
        exchange="client_stream",
    )

    assert unary.kind == "http"
    assert unary.family == "response"
    assert unary.selector == "POST /items"
    assert unary.headers["content-type"] == "application/json"
    assert unary.query == {"a": ["1"]}
    assert stream.kind == "stream"
    assert stream.family == "stream"
    assert upload.kind == "stream"
    assert upload.family == "stream"
    assert upload.exchange == "client_stream"


def test_asgi_message_cannot_bypass_kernel_taxonomy() -> None:
    with pytest.raises(ValueError, match="unsupported WebTransport event"):
        validate_webtransport_event_payload(
            event="webtransport.custom.receive",
            channel="receive",
            payload={"session_id": "s1"},
        )

    assert channel_kind("custom", "request_response") == "http"
    assert channel_family("custom", "request_response") == "response"
    assert channel_subevents("custom", "request_response") == (
        "receive",
        "emit",
        "complete",
    )


def test_server_specific_metadata_not_canonical_without_rule() -> None:
    metadata = webtransport_event_metadata(
        direction="receive",
        message={
            "type": "webtransport.datagram.receive",
            "session_id": "s1",
            "datagram_id": "d1",
            "server_private": "trace-only",
        },
    )

    assert metadata["subevent"] == "datagram.received"
    assert metadata["family"] == "datagram"
    assert metadata["lane"] == "datagram"
    assert "server_private" not in metadata


def test_asgi_runtime_projection_uses_runtime_policy_not_table_class() -> None:
    class TableWithTransportHints:
        __tigrbl_channel_kind__ = "websocket"
        __tigrbl_channel_family__ = "socket"
        __tigrbl_exchange__ = "bidirectional_stream"

    env = SimpleNamespace(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/items",
            "state": {"table": TableWithTransportHints},
        }
    )

    channel = build_asgi_channel(env, exchange="request_response")

    assert channel.kind == "http"
    assert channel.family == "response"
    assert channel.exchange == "request_response"
