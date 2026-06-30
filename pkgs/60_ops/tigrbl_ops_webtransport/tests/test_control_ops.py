from __future__ import annotations

import asyncio

import pytest

from tigrbl_ops_webtransport import (
    close_session,
    close_stream,
    open_bidi_stream,
    open_unidi_stream,
)


def test_open_bidi_stream_preserves_initiator_and_framing() -> None:
    result = asyncio.run(
        open_bidi_stream(
            {
                "session_id": "s1",
                "stream_id": "st1",
                "initiator": "server",
                "inner_framing": "jsonrpc",
                "purpose": "control",
            }
        )
    )

    assert result == {
        "control_plane": "webtransport",
        "action": "open_stream",
        "session_id": "s1",
        "stream_id": "st1",
        "stream_kind": "bidi_stream",
        "lane": "bidi_stream",
        "initiator": "server",
        "purpose": "control",
        "inner_framing": "jsonrpc",
    }


@pytest.mark.parametrize(
    ("initiator", "expected"),
    (("client", "unidi_client_stream"), ("server", "unidi_server_stream")),
)
def test_open_unidi_stream_selects_lane_from_initiator(
    initiator: str,
    expected: str,
) -> None:
    result = asyncio.run(open_unidi_stream({"initiator": initiator}))

    assert result["stream_kind"] == expected
    assert result["lane"] == expected
    assert result["initiator"] == initiator


def test_close_stream_and_close_session_return_control_commands() -> None:
    stream = asyncio.run(close_stream({"stream_id": "st1", "code": "0"}))
    session = asyncio.run(close_session({"session_id": "s1", "reason": "done"}))

    assert stream == {
        "control_plane": "webtransport",
        "action": "close_stream",
        "stream_id": "st1",
        "code": 0,
    }
    assert session == {
        "control_plane": "webtransport",
        "action": "close_session",
        "session_id": "s1",
        "reason": "done",
    }


def test_control_ops_reject_non_mapping_payloads() -> None:
    with pytest.raises(TypeError, match="mapping payloads"):
        asyncio.run(open_bidi_stream(["not", "a", "mapping"]))
