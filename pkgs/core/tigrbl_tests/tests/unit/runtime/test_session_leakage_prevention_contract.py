import pytest


pytestmark = pytest.mark.skip(
    reason="Session leakage prevention conformance is not fully implemented yet."
)


def test_session_state_is_partitioned_by_app_router_table_and_op():
    raise NotImplementedError


def test_attempt_cannot_mutate_another_session_state():
    raise NotImplementedError


def test_stream_id_is_owned_by_exact_session_id():
    raise NotImplementedError


def test_datagram_id_is_owned_by_exact_session_id():
    raise NotImplementedError


def test_engine_session_id_is_owned_by_exact_attempt_id():
    raise NotImplementedError


def test_engine_session_cannot_commit_or_rollback_cross_attempt_transaction():
    raise NotImplementedError


def test_trace_and_qlog_events_preserve_session_parentage():
    raise NotImplementedError


def test_retry_cannot_reuse_state_from_unrelated_session():
    raise NotImplementedError


def test_replay_preserves_original_session_parentage_without_mutating_it():
    raise NotImplementedError


def test_closed_session_rejects_payload_without_state_reopen():
    raise NotImplementedError


def test_unsupported_framing_rejection_cannot_transfer_session_ownership():
    raise NotImplementedError


def test_session_leakage_diagnostics_are_deterministic_and_scoped():
    raise NotImplementedError
