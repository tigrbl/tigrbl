"""Planned runtime execution contract conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Runtime execution contract state-machine enforcement is not implemented yet."
)


def test_runtime_execution_state_machine_valid_transitions() -> None:
    """REST create follows the declared runtime execution lifecycle."""


def test_runtime_execution_state_machine_invalid_transitions() -> None:
    """Undocumented lifecycle transitions fail closed."""


def test_operation_attempt_side_effect_parentage() -> None:
    """Persistence side effects are attributed to one operation attempt."""


def test_engine_session_transaction_lifecycle_contract() -> None:
    """Engine sessions and transactions remain attempt-scoped."""


def test_completion_fence_observed_before_emitted_result() -> None:
    """Completion fence metadata is observed before terminal success."""
