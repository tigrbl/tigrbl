from __future__ import annotations

import pytest

from tigrbl_core._spec import NdjsonFramingSpec, WebTransportBindingSpec, WsBindingSpec
from tigrbl_core._spec.binding_spec import validate_app_framing_for_binding
from tigrbl_kernel.protocol_bindings import compile_binding_protocol_plan
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload
from tigrbl_atoms.runtime_channel import WebTransportSessionState


def test_unknown_transport_framing_rejects_before_dispatch() -> None:
    with pytest.raises(ValueError, match="unsupported app-level framing"):
        validate_app_framing_for_binding(binding_kind="http.rest", framing="jsonrpc")


def test_websocket_ndjson_framing_derives_subprotocol() -> None:
    binding = WsBindingSpec(proto="ws", path="/socket", framing=NdjsonFramingSpec())

    assert binding.framing == "ndjson"
    assert binding.subprotocols == ("ndjson",)


def test_websocket_jsonrpc_profile_rejects_conflicting_subprotocol() -> None:
    with pytest.raises(ValueError, match="conflicts with subprotocols"):
        WsBindingSpec(
            proto="ws",
            path="/socket",
            framing="jsonrpc",
            subprotocols=("graphql-ws",),
        )


def test_webtransport_stream_rejects_datagram_framing() -> None:
    with pytest.raises(ValueError, match="datagram_id"):
        validate_webtransport_event_payload(
            event="webtransport.stream.receive",
            channel="receive",
            payload={
                "session_id": "s1",
                "stream_id": "st1",
                "stream_direction": "bidi",
                "datagram_id": "dg1",
            },
        )


def test_webtransport_datagram_rejects_stream_framing() -> None:
    with pytest.raises(ValueError, match="stream_id"):
        validate_webtransport_event_payload(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s1", "stream_id": "st1", "datagram_id": "dg1"},
        )


def test_http_jsonrpc_rejects_rest_body_framing_fallback() -> None:
    with pytest.raises(ValueError, match="requires method"):
        compile_binding_protocol_plan("Rpc.bad", {"kind": "http.jsonrpc", "path": "/rpc"})


def test_sse_rejects_jsonrpc_message_framing_fallback() -> None:
    with pytest.raises(ValueError, match="unsupported app-level framing"):
        compile_binding_protocol_plan(
            "Events.bad",
            {"kind": "http.sse", "path": "/events", "framing": "jsonrpc"},
        )


def test_binding_token_lowering_records_unsupported_framing_provenance() -> None:
    with pytest.raises(ValueError, match="inner framing"):
        WebTransportBindingSpec(profile="datagram", inner_framing="ndjson")


def test_unsupported_framing_rejection_has_no_persistence_effects() -> None:
    session = WebTransportSessionState(session_id="s1")

    with pytest.raises(ValueError, match="inner framing"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s1", "datagram_id": "dg1", "framing": "ndjson"},
        )

    assert session.snapshot()["datagrams_seen"] == ()


def test_unsupported_framing_rejection_has_no_session_state_leakage() -> None:
    session = WebTransportSessionState(session_id="s1")

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={"session_id": "s2", "stream_id": "st1", "stream_direction": "bidi"},
        )

    assert session.snapshot()["streams"] == {}


def test_unsupported_framing_diagnostics_are_deterministic() -> None:
    bad = {"kind": "webtransport", "profile": "bidi_stream", "framing": "jsonrpc"}

    for _ in range(2):
        with pytest.raises(ValueError, match="framing"):
            compile_binding_protocol_plan("Transport.bad", bad)


def test_unsupported_framing_replay_is_not_admitted() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.close",
        channel="send",
        payload={"session_id": "s1"},
    )

    with pytest.raises(ValueError, match="closed"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi"},
        )
