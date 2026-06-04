"""Planned conformance coverage for runtime retry semantics."""

import pytest


pytestmark = pytest.mark.skip(reason="Runtime retry conformance is not fully implemented yet.")


def test_retry_policy_is_declared_before_attempt_execution() -> None:
    raise NotImplementedError


def test_retry_without_declared_policy_fails_closed_before_side_effects() -> None:
    raise NotImplementedError


def test_retry_attempts_preserve_original_attempt_parentage() -> None:
    raise NotImplementedError


def test_retry_budget_and_max_attempts_are_enforced() -> None:
    raise NotImplementedError


def test_retry_backoff_schedule_is_declared_and_deterministic() -> None:
    raise NotImplementedError


def test_only_declared_retryable_failures_are_retried() -> None:
    raise NotImplementedError


def test_mutation_retry_requires_idempotency_or_replay_policy() -> None:
    raise NotImplementedError


def test_retry_does_not_cross_session_stream_datagram_or_engine_session_scope() -> None:
    raise NotImplementedError


def test_transport_retry_and_runtime_retry_have_single_owner() -> None:
    raise NotImplementedError


def test_retry_reuses_no_open_transaction_from_failed_attempt() -> None:
    raise NotImplementedError


def test_retry_trace_qlog_records_all_attempts_and_decisions() -> None:
    raise NotImplementedError


def test_unsupported_framing_and_closed_session_are_not_retried() -> None:
    raise NotImplementedError
