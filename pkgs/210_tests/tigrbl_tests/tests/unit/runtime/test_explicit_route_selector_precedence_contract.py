"""Planned explicit route and selector precedence conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Explicit route and selector precedence enforcement is not implemented yet."
)


def test_rest_jsonrpc_selectors_are_separate_namespaces() -> None:
    """REST and JSON-RPC selector aliases are not cross-namespace collisions."""


def test_same_selector_same_op_id_allowed() -> None:
    """Duplicate selector declarations may compose when they resolve to one op_id."""


def test_same_selector_different_op_id_requires_override() -> None:
    """Same-namespace selector collisions require explicit override metadata."""


def test_generated_crud_cannot_shadow_custom_op_silently() -> None:
    """Generated CRUD bindings cannot shadow custom operation selectors silently."""


def test_nested_router_precedence_visible_in_plan() -> None:
    """Compiled plans expose the selected route source and precedence owner."""


def test_ambiguous_selector_fails_compile() -> None:
    """Ambiguous same-namespace selectors fail during compilation."""
