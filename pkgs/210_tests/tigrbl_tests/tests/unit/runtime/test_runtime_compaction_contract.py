"""Planned conformance coverage for runtime compaction semantics."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Runtime compaction conformance is not fully implemented yet."
)


def test_runtime_compaction_requires_declared_compaction_policy() -> None:
    raise NotImplementedError


def test_runtime_compaction_preserves_required_semantic_and_concrete_identity() -> None:
    raise NotImplementedError


def test_runtime_compaction_preserves_replay_and_trace_qlog_drillback() -> None:
    raise NotImplementedError


def test_runtime_compaction_does_not_compact_open_attempt_or_unfenced_effects() -> None:
    raise NotImplementedError


def test_runtime_compaction_rollup_operators_are_deterministic_and_order_stable() -> None:
    raise NotImplementedError


def test_runtime_compaction_rejects_mixed_schema_plan_or_runtime_scope() -> None:
    raise NotImplementedError


def test_runtime_compaction_preserves_idempotency_retry_and_replay_parentage() -> None:
    raise NotImplementedError


def test_runtime_compaction_preserves_session_and_engine_session_isolation() -> None:
    raise NotImplementedError


def test_runtime_compaction_applies_redaction_before_persistence_or_export() -> None:
    raise NotImplementedError


def test_runtime_compaction_keeps_cross_transport_equivalence_manifests_comparable() -> None:
    raise NotImplementedError


def test_runtime_compaction_records_compaction_manifest_and_source_ranges() -> None:
    raise NotImplementedError


def test_runtime_compaction_fails_closed_for_unsupported_or_lossy_policy() -> None:
    raise NotImplementedError
