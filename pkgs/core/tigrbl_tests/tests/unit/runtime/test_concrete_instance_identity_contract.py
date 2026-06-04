"""Planned concrete instance identity conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Concrete instance identity enforcement is not implemented yet."
)


def test_semantic_id_stability_across_transports() -> None:
    """Same compiled app yields stable semantic ids across supported bindings."""


def test_concrete_id_uniqueness_within_parent_scope() -> None:
    """Concrete ids are unique within their declared parent scope."""


def test_attempt_id_links_to_op_table_router_app() -> None:
    """Attempt trace records attempt_id to semantic owner parentage."""


def test_atom_execution_links_to_atom_id_and_runtime_plan() -> None:
    """Atom trace records atom_id, attempt_id, and runtime_plan_id."""


def test_replay_id_preserves_original_attempt_id() -> None:
    """Replay records link replay_id to original_attempt_id."""
