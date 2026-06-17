from __future__ import annotations

import pytest

from tigrbl_core._spec.binding_spec import (
    WEBTRANSPORT_INNER_FRAMING_SUPPORT,
    WEBTRANSPORT_LANE_EXCHANGES,
    WEBTRANSPORT_NATIVE_LANES,
    WebTransportBindingSpec,
    project_binding_runtime_metadata,
    validate_webtransport_inner_framing,
    validate_webtransport_lane_exchange,
)
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload


def test_webtransport_native_lane_table_has_no_message_lane() -> None:
    assert WEBTRANSPORT_NATIVE_LANES == (
        "session",
        "bidi_stream",
        "unidi_client_stream",
        "unidi_server_stream",
        "datagram",
    )
    assert "message" not in WEBTRANSPORT_NATIVE_LANES
    assert set(WEBTRANSPORT_INNER_FRAMING_SUPPORT) == set(WEBTRANSPORT_NATIVE_LANES)
    assert set(WEBTRANSPORT_LANE_EXCHANGES) == set(WEBTRANSPORT_NATIVE_LANES)


def test_webtransport_bindingspec_defaults_to_session_lane_and_outer_framing() -> None:
    binding = WebTransportBindingSpec(path="/transport")

    assert binding.profile == "webtransport"
    assert binding.lane == "session"
    assert binding.framing == "webtransport"
    assert binding.inner_framing is None

    metadata = project_binding_runtime_metadata(binding)
    assert metadata["family"] == "session"
    assert metadata["lane"] == "session"
    assert metadata["framing"] == "webtransport"


@pytest.mark.parametrize(
    ("profile", "expected_exchange", "expected_family", "inner_framing"),
    (
        ("bidi_stream", "bidirectional_stream", "stream", "jsonrpc"),
        ("unidi_client_stream", "client_stream", "stream", "ndjson"),
        ("unidi_server_stream", "server_stream", "stream", "text"),
        ("datagram", "bidirectional_stream", "datagram", "json"),
    ),
)
def test_webtransport_lane_specs_project_family_exchange_and_inner_framing(
    profile: str,
    expected_exchange: str,
    expected_family: str,
    inner_framing: str,
) -> None:
    binding = WebTransportBindingSpec(profile=profile, inner_framing=inner_framing)

    metadata = project_binding_runtime_metadata(binding)

    assert binding.lane == profile
    assert binding.exchange == expected_exchange
    assert metadata["family"] == expected_family
    assert metadata["lane"] == profile
    assert metadata["inner_framing"] == inner_framing


def test_webtransport_inner_framing_is_lane_gated() -> None:
    assert (
        validate_webtransport_inner_framing(
            lane="bidi_stream",
            inner_framing="jsonrpc",
        )
        == "jsonrpc"
    )
    assert (
        validate_webtransport_inner_framing(
            lane="datagram",
            inner_framing="json",
        )
        == "json"
    )

    with pytest.raises(ValueError, match="session lane"):
        validate_webtransport_inner_framing(lane="session", inner_framing="json")
    with pytest.raises(ValueError, match="inner framing"):
        validate_webtransport_inner_framing(lane="datagram", inner_framing="jsonrpc")
    with pytest.raises(ValueError, match="inner framing"):
        validate_webtransport_inner_framing(lane="datagram", inner_framing="ndjson")


@pytest.mark.parametrize(
    ("lane", "exchange"),
    (
        ("session", "bidirectional_stream"),
        ("bidi_stream", "bidirectional_stream"),
        ("unidi_client_stream", "client_stream"),
        ("unidi_server_stream", "server_stream"),
        ("datagram", "bidirectional_stream"),
    ),
)
def test_webtransport_lane_exchange_matrix_is_fail_closed(
    lane: str,
    exchange: str,
) -> None:
    assert validate_webtransport_lane_exchange(lane=lane, exchange=exchange) == exchange


@pytest.mark.parametrize(
    ("lane", "bad_exchange"),
    (
        ("session", "client_stream"),
        ("bidi_stream", "server_stream"),
        ("unidi_client_stream", "server_stream"),
        ("unidi_server_stream", "client_stream"),
        ("datagram", "client_stream"),
    ),
)
def test_webtransport_lane_exchange_negative_corpus(
    lane: str,
    bad_exchange: str,
) -> None:
    with pytest.raises(ValueError, match="WebTransport exchange"):
        validate_webtransport_lane_exchange(lane=lane, exchange=bad_exchange)

    with pytest.raises(ValueError, match="WebTransport exchange"):
        WebTransportBindingSpec(profile=lane, exchange=bad_exchange)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="WebTransport exchange|unsupported"):
        compile_binding_protocol_plan(
            "Transport.bad",
            {"kind": "webtransport", "profile": lane, "exchange": bad_exchange},
        )


def test_webtransport_profile_lane_disagreement_fails_closed() -> None:
    with pytest.raises(ValueError, match="conflicts"):
        WebTransportBindingSpec(profile="bidi_stream", lane="datagram")

    binding = WebTransportBindingSpec(profile="webtransport", lane="bidi_stream")
    assert binding.lane == "bidi_stream"
    assert binding.exchange == "bidirectional_stream"


def test_webtransport_rejects_message_profile_and_outer_framing_confusion() -> None:
    with pytest.raises(ValueError, match="message lane"):
        WebTransportBindingSpec(profile="message")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="framing"):
        WebTransportBindingSpec(profile="bidi_stream", framing="jsonrpc")

    with pytest.raises(ValueError, match="framing|outer"):
        compile_binding_protocol_plan(
            "Transport.bad",
            {"kind": "webtransport", "profile": "bidi_stream", "framing": "jsonrpc"},
        )


@pytest.mark.parametrize(
    ("binding", "family", "expected_subevents"),
    (
        (
            {"kind": "webtransport", "profile": "webtransport"},
            "session",
            {"session.open", "session.close"},
        ),
        (
            {"kind": "webtransport", "profile": "bidi_stream", "inner_framing": "jsonrpc"},
            "stream",
            {"stream.open", "stream.chunk.received", "stream.chunk.emit", "stream.close"},
        ),
        (
            {"kind": "webtransport", "profile": "unidi_client_stream", "inner_framing": "ndjson"},
            "stream",
            {"stream.open", "stream.chunk.received", "stream.close"},
        ),
        (
            {"kind": "webtransport", "profile": "unidi_server_stream", "inner_framing": "text"},
            "stream",
            {"stream.open", "stream.chunk.emit", "stream.emit_complete", "stream.close"},
        ),
        (
            {"kind": "webtransport", "profile": "datagram", "inner_framing": "json"},
            "datagram",
            {"datagram.received", "datagram.emit", "datagram.emit_complete"},
        ),
    ),
)
def test_kernel_plan_compiles_webtransport_native_lanes(
    binding: dict[str, object],
    family: str,
    expected_subevents: set[str],
) -> None:
    plan = compile_binding_protocol_plan("Transport.op", binding)

    assert plan["family"] == family
    assert plan["framing"] == "webtransport"
    expected_lane = "session" if binding.get("profile") == "webtransport" else binding.get("profile")
    assert plan["event_key_inputs"]["lane"] == expected_lane
    assert {row["subevent"] for row in plan["lifecycle_rows"]} == expected_subevents
    assert all(row["family"] == family for row in plan["lifecycle_rows"])


def test_kernel_plan_rejects_webtransport_message_lane() -> None:
    with pytest.raises(ValueError, match="message lane"):
        compile_binding_protocol_plan(
            "Transport.bad",
            {"kind": "webtransport", "profile": "message"},
        )


@pytest.mark.parametrize(
    ("event", "channel", "payload", "expected"),
    (
        (
            "webtransport.stream.receive",
            "receive",
            {"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi", "framing": "jsonrpc"},
            {
                "family": "stream",
                "lane": "bidi_stream",
                "exchange": "bidirectional_stream",
                "stream_direction": "bidi",
                "direction": "bidirectional",
                "stream_initiator": "client",
            },
        ),
        (
            "webtransport.stream.receive",
            "receive",
            {"session_id": "s1", "stream_id": "st2", "stream_direction": "client_to_server", "framing": "ndjson"},
            {
                "family": "stream",
                "lane": "unidi_client_stream",
                "exchange": "client_stream",
                "stream_direction": "client_to_server",
                "direction": "client_to_server",
                "stream_initiator": "client",
            },
        ),
        (
            "webtransport.stream.send",
            "send",
            {"session_id": "s1", "stream_id": "st3", "stream_direction": "server_to_client", "framing": "text"},
            {
                "family": "stream",
                "lane": "unidi_server_stream",
                "exchange": "server_stream",
                "stream_direction": "server_to_client",
                "direction": "server_to_client",
                "stream_initiator": "server",
            },
        ),
        (
            "webtransport.datagram.send",
            "send",
            {"session_id": "s1", "datagram_id": "dg1", "framing": "json"},
            {"family": "datagram", "lane": "datagram", "exchange": "bidirectional_stream"},
        ),
    ),
)
def test_webtransport_event_payload_projects_lane_boundary(
    event: str,
    channel: str,
    payload: dict[str, object],
    expected: dict[str, object],
) -> None:
    assert validate_webtransport_event_payload(
        event=event,
        channel=channel,
        payload=payload,
    ) == expected


@pytest.mark.parametrize(
    ("event", "channel", "payload", "match"),
    (
        (
            "webtransport.stream.receive",
            "receive",
            {"session_id": "s1", "stream_direction": "bidi"},
            "stream_id",
        ),
        (
            "webtransport.stream.receive",
            "receive",
            {"session_id": "s1", "stream_id": "st1"},
            "stream_direction",
        ),
        (
            "webtransport.stream.receive",
            "receive",
            {"session_id": "s1", "stream_id": "st1", "stream_direction": "server_to_client"},
            "server_to_client",
        ),
        (
            "webtransport.stream.send",
            "send",
            {"session_id": "s1", "stream_id": "st1", "stream_direction": "client_to_server"},
            "client_to_server",
        ),
        (
            "webtransport.datagram.receive",
            "receive",
            {"session_id": "s1", "stream_id": "st1", "datagram_id": "dg1"},
            "stream_id",
        ),
        (
            "webtransport.stream.send",
            "send",
            {"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi", "datagram_id": "dg1"},
            "datagram_id",
        ),
        (
            "webtransport.stream.receive",
            "receive",
            {
                "session_id": "s1",
                "stream_id": "st1",
                "stream_direction": "client_to_server",
                "stream_initiator": "server",
            },
            "stream_initiator",
        ),
        (
            "webtransport.datagram.send",
            "send",
            {"session_id": "s1", "datagram_id": "dg1", "framing": "jsonrpc"},
            "inner framing",
        ),
        (
            "webtransport.message.receive",
            "receive",
            {"session_id": "s1"},
            "message",
        ),
    ),
)
def test_webtransport_event_payload_negative_corpus(
    event: str,
    channel: str,
    payload: dict[str, object],
    match: str,
) -> None:
    with pytest.raises(ValueError, match=match):
        validate_webtransport_event_payload(event=event, channel=channel, payload=payload)
