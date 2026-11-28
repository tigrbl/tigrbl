from __future__ import annotations

import pytest

from tigrbl_kernel.runtime_contracts import compile_retry_policy, evaluate_retry_attempts


def _policy():
    return compile_retry_policy(
        max_attempts=3,
        retryable_errors=("timeout", "temporarily_unavailable"),
        backoff_ms=(10, 20),
    )


def test_retry_policy_is_declared_before_attempt_execution() -> None:
    with pytest.raises(ValueError, match="retry policy is required"):
        evaluate_retry_attempts(policy=None, failures=("timeout",), idempotency_key="k1")


def test_retry_without_declared_policy_fails_closed_before_side_effects() -> None:
    with pytest.raises(ValueError, match="retry policy is required"):
        evaluate_retry_attempts(policy=None, failures=("timeout",))


def test_retry_attempts_preserve_original_attempt_parentage() -> None:
    attempts = evaluate_retry_attempts(
        policy=_policy(),
        failures=("timeout",),
        idempotency_key="k1",
        original_attempt_id="attempt-root",
    )

    assert attempts[1]["parent_attempt_id"] == "attempt-root"


def test_retry_budget_and_max_attempts_are_enforced() -> None:
    attempts = evaluate_retry_attempts(
        policy=_policy(),
        failures=("timeout", "timeout", "timeout"),
        idempotency_key="k1",
    )

    assert attempts[-1]["decision"] == "budget-exhausted"


def test_retry_backoff_schedule_is_declared_and_deterministic() -> None:
    first = evaluate_retry_attempts(policy=_policy(), failures=("timeout", "timeout"), idempotency_key="k1")
    second = evaluate_retry_attempts(policy=_policy(), failures=("timeout", "timeout"), idempotency_key="k1")

    assert tuple(item["backoff_ms"] for item in first) == (0, 10, 20)
    assert first == second


def test_only_declared_retryable_failures_are_retried() -> None:
    attempts = evaluate_retry_attempts(policy=_policy(), failures=("validation_error",), idempotency_key="k1")

    assert attempts[1]["decision"] == "stop"


def test_mutation_retry_requires_idempotency_or_replay_policy() -> None:
    with pytest.raises(ValueError, match="idempotency key or replay policy"):
        evaluate_retry_attempts(policy=_policy(), failures=("timeout",))


def test_retry_does_not_cross_session_stream_datagram_or_engine_session_scope() -> None:
    with pytest.raises(ValueError, match="cannot cross session"):
        evaluate_retry_attempts(
            policy=_policy(),
            failures=("timeout",),
            idempotency_key="k1",
            session_scope="session-1",
            retry_session_scope="session-2",
        )


def test_transport_retry_and_runtime_retry_have_single_owner() -> None:
    with pytest.raises(ValueError, match="retry owner must be runtime"):
        compile_retry_policy(
            max_attempts=2,
            retryable_errors=("timeout",),
            backoff_ms=(1,),
            owner="transport",
        )


def test_retry_reuses_no_open_transaction_from_failed_attempt() -> None:
    with pytest.raises(ValueError, match="open transaction"):
        evaluate_retry_attempts(
            policy=_policy(),
            failures=("timeout",),
            idempotency_key="k1",
            transaction_open=True,
        )


def test_retry_trace_qlog_records_all_attempts_and_decisions() -> None:
    attempts = evaluate_retry_attempts(policy=_policy(), failures=("timeout",), idempotency_key="k1")

    assert tuple(item["decision"] for item in attempts) == ("original", "retry")


def test_unsupported_framing_and_closed_session_are_not_retried() -> None:
    attempts = evaluate_retry_attempts(
        policy=_policy(),
        failures=("unsupported_framing",),
        idempotency_key="k1",
    )

    assert attempts[1]["decision"] == "stop"
