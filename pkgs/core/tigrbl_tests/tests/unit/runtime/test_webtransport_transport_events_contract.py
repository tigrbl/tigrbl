from __future__ import annotations

import importlib

import pytest


def _require(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        pytest.xfail(f"{module_name} is not implemented")
    value = getattr(module, attr_name, None)
    if value is None:
        pytest.xfail(f"{module_name}.{attr_name} is not implemented")
    return value


def test_webtransport_session_events_follow_open_accept_ready_close_order() -> None:
    compile_events = _require("tigrbl_kernel.webtransport_events", "compile_webtransport_events")

    events = compile_events(surface="session")

    assert [event["subevent"] for event in events] == [
        "session.open",
        "session.accept",
        "session.ready",
        "session.close",
    ]
    assert events[0]["atom"] == "transport.accept"
    assert events[-1]["atom"] == "transport.close"


def test_webtransport_stream_events_cover_receive_send_and_completion() -> None:
    compile_events = _require("tigrbl_kernel.webtransport_events", "compile_webtransport_events")

    events = compile_events(surface="stream")
    subevents = {event["subevent"] for event in events}

    assert {
        "stream.open",
        "stream.chunk.received",
        "stream.chunk.emit",
        "stream.emit_complete",
        "stream.close",
    } <= subevents


def test_webtransport_datagram_events_cover_receive_send_and_completion() -> None:
    compile_events = _require("tigrbl_kernel.webtransport_events", "compile_webtransport_events")

    events = compile_events(surface="datagram")
    subevents = {event["subevent"] for event in events}

    assert {"datagram.received", "datagram.emit", "datagram.emit_complete"} <= subevents
    assert all(event["family"] == "datagram" for event in events)


def test_webtransport_app_frame_events_cover_decode_encode_paths() -> None:
    compile_events = _require("tigrbl_kernel.webtransport_events", "compile_webtransport_events")

    events = compile_events(surface="app_frame")
    anchors = [event["atom"] for event in events]

    assert "framing.decode" in anchors
    assert "framing.encode" in anchors
    assert "transport.emit" in anchors


def test_webtransport_event_order_places_disconnect_after_stream_and_datagram_completion() -> None:
    compile_chain = _require("tigrbl_kernel.webtransport_events", "compile_webtransport_chain")

    chain = compile_chain(include_stream=True, include_datagram=True)
    subevents = chain["subevents"]

    assert subevents.index("stream.emit_complete") < subevents.index("session.close")
    assert subevents.index("datagram.emit_complete") < subevents.index("session.close")


def test_webtransport_scope_validation_rejects_missing_quic_metadata() -> None:
    validate_scope = _require("tigrbl_runtime.protocol.webtransport", "validate_webtransport_scope")

    with pytest.raises(ValueError, match="webtransport|quic|scope|metadata"):
        validate_scope({"type": "webtransport", "path": "/transport"})
