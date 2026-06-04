"""Planned table profile operation selection matrix conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Table profile operation selection matrix enforcement is not implemented yet."
)


def test_abstract_crud_profile_selects_crud_ops_without_transport_bindings():
    raise NotImplementedError


def test_abstract_realtime_profile_selects_realtime_ops_without_transport_bindings():
    raise NotImplementedError


def test_bulk_crud_profile_selects_bulk_and_crud_ops():
    raise NotImplementedError


def test_oltp_profile_selects_transactional_query_and_merge_ops():
    raise NotImplementedError


def test_olap_profile_selects_read_only_analytical_ops():
    raise NotImplementedError


def test_checkpoint_profile_selects_checkpoint_ops_only():
    raise NotImplementedError


def test_abstract_profiles_do_not_emit_concrete_binding_tokens():
    raise NotImplementedError


def test_olap_profile_rejects_mutation_ops():
    raise NotImplementedError


def test_datagram_profile_rejects_stream_and_session_ops():
    raise NotImplementedError


def test_custom_ops_are_not_selected_by_profile_defaults():
    raise NotImplementedError


def test_unknown_table_profile_fails_closed():
    raise NotImplementedError


def test_profile_operation_selection_is_deterministic():
    raise NotImplementedError
