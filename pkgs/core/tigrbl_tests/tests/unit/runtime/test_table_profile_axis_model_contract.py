"""Planned table profile axis model conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Table profile axis model enforcement is not implemented yet."
)


def test_table_profile_axis_model_separates_concerns() -> None:
    """Profile config keeps op selection, bindings, docs, and exposure separate."""


def test_binding_profile_does_not_imply_ops_docs_or_network() -> None:
    """A binding profile token does not implicitly enable ops, docs, or mounting."""


def test_default_bindings_do_not_override_per_op_bindings() -> None:
    """Per-op bindings remain a distinct axis from blanket table defaults."""
