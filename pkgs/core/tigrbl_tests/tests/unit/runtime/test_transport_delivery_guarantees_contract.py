import pytest


pytestmark = pytest.mark.skip(
    reason="Transport delivery guarantee enforcement is not implemented yet."
)


def test_each_transport_binding_declares_delivery_guarantees():
    raise NotImplementedError


def test_http_request_response_declares_single_attempt_no_transport_retry():
    raise NotImplementedError


def test_http_stream_preserves_chunk_order_within_attempt():
    raise NotImplementedError


def test_sse_preserves_event_order_and_reconnect_cursor_policy():
    raise NotImplementedError


def test_websocket_preserves_message_order_per_connection_lane():
    raise NotImplementedError


def test_webtransport_stream_preserves_order_per_stream_id():
    raise NotImplementedError


def test_webtransport_datagram_declares_unordered_unreliable_delivery():
    raise NotImplementedError


def test_retry_requires_idempotency_or_declared_replay_policy():
    raise NotImplementedError


def test_replay_uses_attempt_session_stream_and_trace_identity():
    raise NotImplementedError


def test_delivery_guarantees_reject_unsupported_exactly_once_claims():
    raise NotImplementedError


def test_cross_session_delivery_state_cannot_leak():
    raise NotImplementedError


def test_delivery_diagnostics_report_ordering_retry_and_replay_sources():
    raise NotImplementedError
