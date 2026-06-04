"""Planned operation verb to default binding matrix conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Operation verb to default binding matrix enforcement is not implemented yet."
)


def test_create_read_update_delete_list_verbs_lower_to_rest_and_jsonrpc_defaults():
    raise NotImplementedError


def test_bulk_verbs_lower_to_bulk_rest_and_jsonrpc_defaults():
    raise NotImplementedError


def test_query_and_merge_verbs_lower_to_query_compatible_defaults():
    raise NotImplementedError


def test_stream_verbs_lower_to_stream_compatible_defaults():
    raise NotImplementedError


def test_sse_verbs_lower_to_sse_compatible_defaults():
    raise NotImplementedError


def test_websocket_jsonrpc_verbs_require_jsonrpc_framing_defaults():
    raise NotImplementedError


def test_webtransport_stream_verbs_lower_to_lane_compatible_defaults():
    raise NotImplementedError


def test_webtransport_datagram_verbs_lower_to_datagram_only_defaults():
    raise NotImplementedError


def test_explicit_opspec_bindings_override_verb_defaults():
    raise NotImplementedError


def test_custom_verbs_do_not_receive_implicit_defaults():
    raise NotImplementedError


def test_unknown_verb_default_binding_fails_closed():
    raise NotImplementedError


def test_incompatible_verb_profile_binding_fails_closed():
    raise NotImplementedError


def test_default_binding_matrix_output_is_deterministic():
    raise NotImplementedError
