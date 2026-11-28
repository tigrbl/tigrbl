"""Planned conformance coverage for runtime rollup semantics."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Runtime rollup conformance is not fully implemented yet."
)


def test_runtime_rollup_requires_declared_rollup_policy() -> None:
    raise NotImplementedError


def test_runtime_rollup_preserves_required_identity_dimensions() -> None:
    raise NotImplementedError


def test_runtime_rollup_operators_are_deterministic_and_order_stable() -> None:
    raise NotImplementedError


def test_runtime_rollup_rejects_mixed_schema_plan_or_scope_without_merge_policy() -> None:
    raise NotImplementedError


def test_runtime_rollup_preserves_replay_trace_qlog_and_audit_drillback() -> None:
    raise NotImplementedError


def test_runtime_rollup_preserves_idempotency_retry_and_replay_counts_and_parentage() -> None:
    raise NotImplementedError


def test_runtime_rollup_preserves_error_diagnostic_and_effect_summary_classes() -> None:
    raise NotImplementedError


def test_runtime_rollup_preserves_session_and_engine_session_isolation() -> None:
    raise NotImplementedError


def test_runtime_rollup_applies_redaction_before_export_or_persistence() -> None:
    raise NotImplementedError


def test_runtime_rollup_keeps_cross_transport_equivalence_summaries_comparable() -> None:
    raise NotImplementedError


def test_runtime_rollup_manifest_records_policy_operator_and_source_ranges() -> None:
    raise NotImplementedError


def test_runtime_rollup_fails_closed_for_unsupported_operator_or_lossy_summary() -> None:
    raise NotImplementedError
