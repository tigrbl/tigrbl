"""Planned table transport binding profile conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Table transport binding profile enforcement is not implemented yet."
)


def test_crudtable_abstract_selects_ops_without_bindings():
    raise NotImplementedError


def test_realtimetable_abstract_selects_ops_without_bindings():
    raise NotImplementedError


def test_resttable_lowers_to_http_rest_bindings():
    raise NotImplementedError


def test_jsonrpctable_lowers_to_http_jsonrpc_bindings():
    raise NotImplementedError


def test_bulkcrudtable_includes_bulk_ops():
    raise NotImplementedError


def test_oltptable_includes_query_and_merge_ops():
    raise NotImplementedError


def test_olaptable_selects_olap_query_ops():
    raise NotImplementedError


def test_streamtable_op_binding_compatibility():
    raise NotImplementedError


def test_ssetable_op_binding_compatibility():
    raise NotImplementedError


def test_websocket_jsonrpc_table_requires_subprotocol():
    raise NotImplementedError


def test_webtransport_session_table_selects_session_compatible_ops():
    raise NotImplementedError


def test_webtransport_bidi_table_selects_stream_compatible_ops():
    raise NotImplementedError


def test_webtransport_client_stream_table_selects_upload_ops():
    raise NotImplementedError


def test_webtransport_server_stream_table_selects_download_ops():
    raise NotImplementedError


def test_webtransport_datagram_table_selects_send_datagram_only():
    raise NotImplementedError


def test_binding_token_lowering_is_deterministic():
    raise NotImplementedError


def test_explicit_opspec_bindings_override_table_defaults():
    raise NotImplementedError


def test_docs_exposure_does_not_imply_network_mount():
    raise NotImplementedError


def test_network_exposure_does_not_imply_docs_exposure():
    raise NotImplementedError


def test_asgi_transport_is_not_table_class():
    raise NotImplementedError


def test_custom_op_remains_explicit_only():
    raise NotImplementedError


def test_checkpoint_profile_policy_is_enforced():
    raise NotImplementedError
