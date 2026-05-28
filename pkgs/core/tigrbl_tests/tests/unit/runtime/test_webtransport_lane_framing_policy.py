from __future__ import annotations

import pytest

from tigrbl_core._spec.binding_spec import (
    WEBTRANSPORT_INNER_FRAMING_SUPPORT,
    WEBTRANSPORT_NATIVE_LANES,
    WebTransportBindingSpec,
    project_binding_runtime_metadata,
    validate_webtransport_inner_framing,
)
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan


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
