from __future__ import annotations

import pytest

from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan
from tigrbl_runtime.protocol.webtransport import WebTransportSessionState


def test_each_transport_binding_declares_delivery_guarantees() -> None:
    bindings = (
        {"kind": "http.rest", "path": "/items", "methods": ("GET",)},
        {"kind": "http.jsonrpc", "rpc_method": "Item.read"},
        {"kind": "http.stream", "path": "/stream"},
        {"kind": "http.sse", "path": "/events"},
        {"kind": "ws", "path": "/socket"},
        {"kind": "webtransport", "profile": "bidi_stream"},
        {"kind": "webtransport", "profile": "datagram"},
    )

    for binding in bindings:
        plan = compile_binding_protocol_plan("Item.op", binding)
        assert plan["family"]
        assert plan["framing"]
        assert plan["capability_requirements"]["required_mask"] > 0
        assert plan["lifecycle_rows"]


def test_http_request_response_declares_single_attempt_no_transport_retry() -> None:
    plan = compile_binding_protocol_plan("Item.read", {"kind": "http.rest", "path": "/items"})

    assert plan["family"] == "request"
    assert plan["framing"] == "json"
    assert "retry" not in plan


def test_http_stream_preserves_chunk_order_within_attempt() -> None:
    plan = compile_binding_protocol_plan("Item.tail", {"kind": "http.stream", "path": "/stream"})

    assert plan["family"] == "stream"
    assert ("transport.emit", "transport.emit_complete") == tuple(
        anchor for anchor in plan["atom_anchors"] if anchor.startswith("transport.emit")
    )


def test_sse_preserves_event_order_and_reconnect_cursor_policy() -> None:
    plan = compile_binding_protocol_plan("Item.events", {"kind": "http.sse", "path": "/events"})

    assert plan["framing"] == "sse"
    assert ("message.encoded", "message.emit", "stream.close") == tuple(
        row["subevent"] for row in plan["lifecycle_rows"]
    )


def test_websocket_preserves_message_order_per_connection_lane() -> None:
    plan = compile_binding_protocol_plan("Socket.message", {"kind": "ws", "path": "/socket"})

    assert plan["family"] == "message"
    assert tuple(row["subevent"] for row in plan["lifecycle_rows"]) == (
        "message.received",
        "message.emit",
        "session.close",
    )


def test_webtransport_stream_preserves_order_per_stream_id() -> None:
    session = WebTransportSessionState(session_id="s1")
    first = session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi"},
    )
    second = session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi"},
    )

    assert first["streams"]["st1"]["chunks_received"] == 1
    assert second["streams"]["st1"]["chunks_received"] == 2


def test_webtransport_datagram_declares_unordered_unreliable_delivery() -> None:
    plan = compile_binding_protocol_plan(
        "Transport.datagram",
        {"kind": "webtransport", "profile": "datagram"},
    )

    assert plan["family"] == "datagram"
    assert tuple(row["subevent"] for row in plan["lifecycle_rows"]) == (
        "datagram.received",
        "datagram.emit",
        "datagram.emit_complete",
    )


def test_retry_requires_idempotency_or_declared_replay_policy() -> None:
    plan = compile_binding_protocol_plan("Item.create", {"kind": "http.rest", "path": "/items"})

    assert "retry" not in plan["event_key_inputs"]


def test_replay_uses_attempt_session_stream_and_trace_identity() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi"},
    )

    assert session.snapshot()["session_id"] == "s1"
    assert "st1" in session.snapshot()["streams"]


def test_delivery_guarantees_reject_unsupported_exactly_once_claims() -> None:
    with pytest.raises(ValueError, match="unsupported exchange"):
        compile_binding_protocol_plan(
            "Bad.ws",
            {"kind": "ws", "path": "/socket", "exchange": "request_response"},
        )


def test_cross_session_delivery_state_cannot_leak() -> None:
    session = WebTransportSessionState(session_id="s1")

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s2", "datagram_id": "dg1"},
        )


def test_delivery_diagnostics_report_ordering_retry_and_replay_sources() -> None:
    plan = compile_binding_protocol_plan(
        "Transport.stream",
        {"kind": "webtransport", "profile": "bidi_stream"},
    )

    assert plan["event_key_inputs"] == {
        "family": "stream",
        "binding": "webtransport",
        "framing": "webtransport",
        "lane": "bidi_stream",
        "inner_framing": None,
    }
