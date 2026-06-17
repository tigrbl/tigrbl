from __future__ import annotations

import pytest

from tigrbl_atoms.runtime_channel import (
    Direction,
    Initiator,
    LaneId,
    StreamIdWidth,
    WebTransportSessionState,
    WebTransportStreamIdProvisioning,
)


def test_lane_id_encodes_uint8_initiator_direction_and_ordinal_examples() -> None:
    control = LaneId.encode(
        initiator=Initiator.CLIENT,
        direction=Direction.BIDI,
        ordinal=0,
    )
    events = LaneId.encode(
        initiator=Initiator.SERVER,
        direction=Direction.UNI,
        ordinal=0,
    )
    logs = LaneId.encode(
        initiator=Initiator.SERVER,
        direction=Direction.UNI,
        ordinal=1,
    )
    upload = LaneId.encode(
        initiator=Initiator.CLIENT,
        direction=Direction.UNI,
        ordinal=0,
    )
    download = LaneId.encode(
        initiator=Initiator.SERVER,
        direction=Direction.UNI,
        ordinal=2,
    )

    assert control.value == 0
    assert events.value == 3
    assert logs.value == 7
    assert upload.value == 2
    assert download.value == 11
    assert logs.initiator is Initiator.SERVER
    assert logs.direction is Direction.UNI
    assert logs.ordinal == 1
    assert LaneId(255).ordinal == 63
    with pytest.raises(ValueError, match="uint8"):
        LaneId(256)
    with pytest.raises(ValueError, match="6 bits"):
        LaneId.encode(
            initiator=Initiator.CLIENT,
            direction=Direction.BIDI,
            ordinal=64,
        )


def test_webtransport_stream_id_provisioning_selects_uint8_or_uint16() -> None:
    compact = WebTransportStreamIdProvisioning(max_streams=256)
    expanded = WebTransportStreamIdProvisioning(max_streams=257)

    assert compact.width is StreamIdWidth.UINT8
    assert compact.lanes_per_transport_class == 64
    assert compact.total_lanes == 256
    assert expanded.width is StreamIdWidth.UINT16
    assert expanded.lanes_per_transport_class == 16_384
    assert expanded.total_lanes == 65_536
    lane = expanded.encode_lane(
        initiator=Initiator.SERVER,
        direction=Direction.UNI,
        ordinal=64,
    )
    assert lane.width is StreamIdWidth.UINT16
    assert lane.value == 259
    assert lane.ordinal == 64
    with pytest.raises(ValueError, match="uint16"):
        WebTransportStreamIdProvisioning(max_streams=65_537)


def test_lane_id_provisioning_rejects_invalid_encoding_inputs() -> None:
    with pytest.raises(ValueError, match="lane_id must be an integer"):
        LaneId(True)
    with pytest.raises(ValueError, match="lane_id must be an integer"):
        LaneId("1")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Initiator"):
        LaneId.encode(initiator=2, direction=Direction.BIDI, ordinal=0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Direction"):
        LaneId.encode(initiator=Initiator.CLIENT, direction=2, ordinal=0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="ordinal must be an integer"):
        LaneId.encode(
            initiator=Initiator.CLIENT,
            direction=Direction.BIDI,
            ordinal=True,  # type: ignore[arg-type]
        )
    with pytest.raises(ValueError, match="14 bits"):
        LaneId.encode(
            initiator=Initiator.CLIENT,
            direction=Direction.BIDI,
            ordinal=16_384,
            width=StreamIdWidth.UINT16,
        )


def test_webtransport_stream_id_provisioning_rejects_invalid_stream_caps() -> None:
    with pytest.raises(ValueError, match="integer"):
        WebTransportStreamIdProvisioning(max_streams=True)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="integer"):
        WebTransportStreamIdProvisioning(max_streams="256")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="between 1 and uint16"):
        WebTransportStreamIdProvisioning(max_streams=0)
    with pytest.raises(ValueError, match="between 1 and uint16"):
        WebTransportStreamIdProvisioning(max_streams=65_537)


def test_webtransport_session_exposes_provisioning_and_caps_distinct_streams() -> None:
    session = WebTransportSessionState(session_id="sess-1", max_streams=2)

    assert session.snapshot()["stream_id_provisioning"] == {
        "max_streams": 2,
        "width": "uint8",
        "lanes_per_transport_class": 64,
        "total_lanes": 256,
    }
    assert session.provision_lane_id(
        initiator=Initiator.CLIENT,
        direction=Direction.BIDI,
        ordinal=0,
    ).value == 0
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "sess-1", "stream_id": "stream-1", "stream_direction": "bidi"},
    )
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "sess-1", "stream_id": "stream-2", "stream_direction": "bidi"},
    )

    with pytest.raises(ValueError, match="max_streams"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={"session_id": "sess-1", "stream_id": "stream-3", "stream_direction": "bidi"},
        )


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
            "stream_initiator": "client",
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
    assert snapshot["streams"]["bidi-1"]["stream_initiator"] == "client"
    assert snapshot["streams"]["bidi-1"]["direction"] == "bidirectional"
    assert snapshot["streams"]["bidi-1"]["chunks_received"] == 1
    assert snapshot["streams"]["client-1"]["lane"] == "unidi_client_stream"
    assert snapshot["streams"]["client-1"]["exchange"] == "client_stream"
    assert snapshot["streams"]["client-1"]["stream_initiator"] == "client"
    assert snapshot["streams"]["server-1"]["lane"] == "unidi_server_stream"
    assert snapshot["streams"]["server-1"]["stream_initiator"] == "server"
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
