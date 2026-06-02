from __future__ import annotations

import pytest

from tigrbl_runtime.protocol.client_session_coverage import (
    ClientSessionRobustnessRecorder,
)


def test_slow_consumer_fast_producer_pressure_is_bounded() -> None:
    harness = ClientSessionRobustnessRecorder()
    harness.open("client-a", "session-a")
    harness.send("client-a", "session-a", "one")
    harness.send("client-a", "session-a", "two")

    with pytest.raises(BufferError, match="bounded queue"):
        harness.send("client-a", "session-a", "three")

    assert harness.sessions["session-a"].payloads == ["one", "two"]
    assert harness.errors[-1]["error_kind"] == "pressure_budget_exceeded"


def test_malformed_payload_and_unsupported_framing_fail_closed() -> None:
    harness = ClientSessionRobustnessRecorder()
    harness.open("client-a", "session-a")

    with pytest.raises(ValueError, match="malformed"):
        harness.send("client-a", "session-a", {})
    with pytest.raises(ValueError, match="unsupported framing"):
        harness.send("client-a", "session-a", "one", framing="ndjson")

    assert [error["error_kind"] for error in harness.errors] == [
        "malformed_payload",
        "unsupported_framing",
    ]


def test_disconnect_timeout_cancel_and_post_close_send_reject() -> None:
    harness = ClientSessionRobustnessRecorder()
    harness.open("client-a", "session-a")
    harness.open("client-b", "session-b")
    harness.timeout("client-a", "session-a")
    harness.cancel("client-b", "session-b")

    with pytest.raises(RuntimeError, match="post-close"):
        harness.send("client-a", "session-a", "late")
    with pytest.raises(RuntimeError, match="post-close"):
        harness.send("client-b", "session-b", "late")

    assert [error["error_kind"] for error in harness.errors] == [
        "timeout",
        "cancelled",
        "post_close_send",
        "post_close_send",
    ]


def test_cross_client_and_cross_session_payloads_are_rejected() -> None:
    harness = ClientSessionRobustnessRecorder()
    harness.open("client-a", "session-a")
    harness.open("client-b", "session-b")

    with pytest.raises(PermissionError, match="cross-client"):
        harness.send("client-a", "session-b", "stolen")

    assert harness.sessions["session-a"].payloads == []
    assert harness.sessions["session-b"].payloads == []
    assert harness.errors[-1]["error_kind"] == "cross_client_session_access"


def test_stream_and_datagram_identifiers_are_preserved_on_t2_failures() -> None:
    harness = ClientSessionRobustnessRecorder(queue_limit=1)
    harness.open("client-a", "session-a")
    harness.send("client-a", "session-a", "one", stream_id="stream-a")

    with pytest.raises(BufferError, match="bounded queue"):
        harness.send(
            "client-a",
            "session-a",
            "two",
            stream_id="stream-a",
            datagram_id="datagram-late",
        )

    assert harness.sessions["session-a"].streams_seen == {"stream-a"}
    assert harness.errors[-1]["stream_id"] == "stream-a"
    assert harness.errors[-1]["datagram_id"] == "datagram-late"
    assert "lane" not in harness.errors[-1]


def test_unknown_session_rejection_is_recorded_fail_closed() -> None:
    harness = ClientSessionRobustnessRecorder()

    with pytest.raises(KeyError, match="unknown session"):
        harness.send("client-a", "missing-session", "late")

    assert harness.errors[-1]["error_kind"] == "unknown_session"
    assert harness.errors[-1]["client_id"] == "client-a"
    assert harness.errors[-1]["session_id"] == "missing-session"
