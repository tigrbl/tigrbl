import pytest


pytestmark = pytest.mark.skip(
    reason="Binding token lowering enforcement is not implemented yet."
)


def test_binding_tokens_have_canonical_shape():
    raise NotImplementedError


def test_table_profile_defaults_lower_to_ordered_binding_tokens():
    raise NotImplementedError


def test_opspec_binding_overrides_are_applied_before_defaults():
    raise NotImplementedError


def test_rest_binding_tokens_include_method_path_and_media_type():
    raise NotImplementedError


def test_jsonrpc_binding_tokens_include_method_and_framing():
    raise NotImplementedError


def test_websocket_binding_tokens_include_framing_and_session_lanes():
    raise NotImplementedError


def test_webtransport_binding_tokens_include_stream_and_datagram_lanes():
    raise NotImplementedError


def test_binding_token_lowering_rejects_unsupported_transport_profile_pairs():
    raise NotImplementedError


def test_binding_token_lowering_rejects_unsupported_framing_fallback():
    raise NotImplementedError


def test_binding_token_lowering_reports_source_precedence():
    raise NotImplementedError


def test_binding_token_lowering_output_is_deterministic():
    raise NotImplementedError


def test_binding_token_lowering_does_not_mutate_source_specs():
    raise NotImplementedError
