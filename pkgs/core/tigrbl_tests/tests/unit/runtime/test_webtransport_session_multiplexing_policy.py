from __future__ import annotations

import pytest

from tigrbl_atoms.runtime_channel import WebTransportSessionState


def test_webtransport_session_tracks_multiple_stream_lanes_and_datagrams_independently() -> None:
    session = WebTransportSessionState(session_id="sess-1")

    session.apply_event(event="webtransport.accept", channel="send", payload={"session_id": "sess-1"})
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={
            "session_id": "sess-1",
            "stream_id": "bidi-1",
            "stream_direction": "bidi",
            "framing": "jsonrpc",
        },
    )
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={
            "session_id": "sess-1",
            "stream_id": "client-1",
            "stream_direction": "client_to_server",
            "framing": "ndjson",
        },
    )
    session.apply_event(
        event="webtransport.stream.send",
        channel="send",
        payload={
            "session_id": "sess-1",
            "stream_id": "server-1",
            "stream_direction": "server_to_client",
            "framing": "text",
        },
    )
    before_datagram = session.snapshot()["streams"]
    session.apply_event(
        event="webtransport.datagram.send",
        channel="send",
        payload={"session_id": "sess-1", "datagram_id": "dg-1", "framing": "json"},
    )

    snapshot = session.snapshot()

    assert snapshot["accepted"] is True
    assert snapshot["streams"] == before_datagram
    assert snapshot["streams"]["bidi-1"]["lane"] == "bidi_stream"
    assert snapshot["streams"]["bidi-1"]["chunks_received"] == 1
    assert snapshot["streams"]["client-1"]["lane"] == "unidi_client_stream"
    assert snapshot["streams"]["client-1"]["exchange"] == "client_stream"
    assert snapshot["streams"]["server-1"]["lane"] == "unidi_server_stream"
    assert snapshot["streams"]["server-1"]["chunks_sent"] == 1
    assert snapshot["datagrams_seen"] == ("dg-1",)


def test_webtransport_session_rejects_lane_metadata_changes_for_existing_stream_id() -> None:
    session = WebTransportSessionState(session_id="sess-1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "sess-1", "stream_id": "stream-1", "stream_direction": "bidi"},
    )

    with pytest.raises(ValueError, match="lane metadata changed"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={
                "session_id": "sess-1",
                "stream_id": "stream-1",
                "stream_direction": "client_to_server",
            },
        )


def test_webtransport_session_close_cascades_to_active_stream_lanes() -> None:
    session = WebTransportSessionState(session_id="sess-1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "sess-1", "stream_id": "bidi-1", "stream_direction": "bidi"},
    )
    session.apply_event(
        event="webtransport.stream.send",
        channel="send",
        payload={"session_id": "sess-1", "stream_id": "server-1", "stream_direction": "server_to_client"},
    )

    snapshot = session.apply_event(
        event="webtransport.close",
        channel="send",
        payload={"session_id": "sess-1"},
    )

    assert snapshot["closed"] is True
    assert all(state["closed"] is True for state in snapshot["streams"].values())
    with pytest.raises(ValueError, match="session is closed"):
        session.apply_event(
            event="webtransport.datagram.send",
            channel="send",
            payload={"session_id": "sess-1", "datagram_id": "dg-2"},
        )


def test_webtransport_session_rejects_cross_session_payloads() -> None:
    session = WebTransportSessionState(session_id="sess-1")

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "sess-2", "datagram_id": "dg-1"},
        )


def test_webtransport_session_close_is_idempotent_but_blocks_further_payload_events() -> None:
    session = WebTransportSessionState(session_id="sess-1")

    session.apply_event(event="webtransport.accept", channel="send", payload={"session_id": "sess-1"})
    first = session.apply_event(
        event="webtransport.close",
        channel="send",
        payload={"session_id": "sess-1"},
    )
    second = session.apply_event(
        event="webtransport.close",
        channel="send",
        payload={"session_id": "sess-1"},
    )

    assert first["closed"] is True
    assert second["closed"] is True
    with pytest.raises(ValueError, match="session is closed"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={"session_id": "sess-1", "stream_id": "bidi-1", "stream_direction": "bidi"},
        )
