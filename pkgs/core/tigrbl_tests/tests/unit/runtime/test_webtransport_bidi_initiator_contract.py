from __future__ import annotations

import pytest

from tigrbl_atoms.runtime_channel import Direction, Initiator, WebTransportSessionState
from tigrbl_kernel.channel_taxonomy import webtransport_event_metadata
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload


def test_webtransport_bidi_projection_distinguishes_client_and_server_initiator() -> None:
    client = validate_webtransport_event_payload(
        event="webtransport.stream.receive",
        channel="receive",
        payload={
            "session_id": "s1",
            "stream_id": "client-bidi",
            "stream_direction": "bidi",
            "stream_initiator": "client",
        },
    )
    server = validate_webtransport_event_payload(
        event="webtransport.stream.send",
        channel="send",
        payload={
            "session_id": "s1",
            "stream_id": "server-bidi",
            "stream_direction": "bidi",
            "stream_initiator": "server",
        },
    )

    assert client["stream_initiator"] == "client"
    assert server["stream_initiator"] == "server"
    assert client["lane"] == server["lane"] == "bidi_stream"
    assert client["exchange"] == server["exchange"] == "bidirectional_stream"


def test_webtransport_metadata_carries_bidi_initiator_to_hook_selectors() -> None:
    metadata = webtransport_event_metadata(
        direction="send",
        message={
            "type": "webtransport.stream.send",
            "session_id": "s1",
            "stream_id": "server-bidi",
            "stream_direction": "bidi",
            "stream_initiator": "server",
            "framing": "json",
        },
    )

    assert metadata["subevent"] == "stream.chunk.emit"
    assert metadata["stream_initiator"] == "server"
    assert metadata["direction"] == "bidirectional"
    assert metadata["lane"] == "bidi_stream"


def test_webtransport_session_snapshot_preserves_bidi_initiator_and_lane_id() -> None:
    session = WebTransportSessionState(session_id="s1")
    lane_id = session.provision_lane_id(
        initiator=Initiator.CLIENT,
        direction=Direction.BIDI,
        ordinal=3,
    )

    first = session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={
            "session_id": "s1",
            "stream_id": "st1",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "lane_id": lane_id.value,
        },
    )
    second = session.apply_event(
        event="webtransport.stream.send",
        channel="send",
        payload={
            "session_id": "s1",
            "stream_id": "st1",
            "stream_direction": "bidi",
            "stream_initiator": "client",
            "lane_id": lane_id.value,
        },
    )

    assert first["streams"]["st1"]["stream_initiator"] == "client"
    assert second["streams"]["st1"]["chunks_sent"] == 1
    assert second["streams"]["st1"]["lane_id"] == lane_id.value
    assert second["streams"]["st1"]["stream_ordinal"] == 3


def test_webtransport_session_rejects_initiator_drift_for_existing_bidi_stream() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={
            "session_id": "s1",
            "stream_id": "st1",
            "stream_direction": "bidi",
            "stream_initiator": "client",
        },
    )

    with pytest.raises(ValueError, match="initiator metadata changed"):
        session.apply_event(
            event="webtransport.stream.send",
            channel="send",
            payload={
                "session_id": "s1",
                "stream_id": "st1",
                "stream_direction": "bidi",
                "stream_initiator": "server",
            },
        )
