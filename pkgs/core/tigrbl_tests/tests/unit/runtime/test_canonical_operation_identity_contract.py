"""Planned canonical operation identity conformance tests."""

import pytest


pytestmark = pytest.mark.skip(
    reason="Canonical operation identity enforcement is not implemented yet."
)


def test_canonical_op_id_stable_across_rest_jsonrpc_ws() -> None:
    """Widget.create resolves to one op_id across supported bindings."""


def test_custom_op_requires_canonical_op_id() -> None:
    """Custom operations must declare or derive a stable canonical op_id."""


def test_openapi_openrpc_runtime_op_id_parity() -> None:
    """Docs operation ids and runtime plan op_id values match."""


def test_transport_selector_aliases_resolve_to_op_id() -> None:
    """Each transport selector alias resolves to the intended op_id."""
