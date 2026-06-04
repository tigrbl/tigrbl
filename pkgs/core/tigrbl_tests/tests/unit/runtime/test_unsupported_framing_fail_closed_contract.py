import pytest


pytestmark = pytest.mark.skip(
    reason="Unsupported framing fail-closed conformance is not fully implemented yet."
)


def test_unknown_transport_framing_rejects_before_dispatch():
    raise NotImplementedError


def test_websocket_ndjson_framing_does_not_fallback_to_text_json():
    raise NotImplementedError


def test_websocket_jsonrpc_profile_rejects_non_jsonrpc_framing():
    raise NotImplementedError


def test_webtransport_stream_rejects_datagram_framing():
    raise NotImplementedError


def test_webtransport_datagram_rejects_stream_framing():
    raise NotImplementedError


def test_http_jsonrpc_rejects_rest_body_framing_fallback():
    raise NotImplementedError


def test_sse_rejects_jsonrpc_message_framing_fallback():
    raise NotImplementedError


def test_binding_token_lowering_records_unsupported_framing_provenance():
    raise NotImplementedError


def test_unsupported_framing_rejection_has_no_persistence_effects():
    raise NotImplementedError


def test_unsupported_framing_rejection_has_no_session_state_leakage():
    raise NotImplementedError


def test_unsupported_framing_diagnostics_are_deterministic():
    raise NotImplementedError


def test_unsupported_framing_replay_is_not_admitted():
    raise NotImplementedError
