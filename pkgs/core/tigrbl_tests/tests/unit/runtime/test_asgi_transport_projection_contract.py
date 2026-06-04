"""Planned ASGI transport projection conformance tests."""

import pytest

pytestmark = pytest.mark.skip(
    reason="ASGI transport projection enforcement is not implemented yet."
)


def test_websocket_receive_projects_message_received() -> None:
    """ASGI websocket.receive projects to the canonical message.received event."""


def test_wt_stream_receive_projects_stream_chunk_received() -> None:
    """WebTransport stream receive projects to stream.chunk.received with ids."""


def test_http_body_stream_projects_by_binding_kind() -> None:
    """HTTP body projection is binding-aware for unary and stream bindings."""


def test_asgi_message_cannot_bypass_kernel_taxonomy() -> None:
    """Unknown ASGI messages cannot create undocumented semantic events."""


def test_server_specific_metadata_not_canonical_without_rule() -> None:
    """Server-specific metadata is trace-only unless a projection rule allows it."""
