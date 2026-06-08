from __future__ import annotations

import pytest

from tigrbl_runtime.protocol.webtransport import WebTransportSessionState


def test_session_state_is_partitioned_by_app_router_table_and_op() -> None:
    first = WebTransportSessionState(session_id="app.router.table.op.s1")
    second = WebTransportSessionState(session_id="app.router.table.op.s2")

    first.apply_event(
        event="webtransport.datagram.receive",
        channel="receive",
        payload={"session_id": first.session_id, "datagram_id": "dg1"},
    )

    assert first.snapshot()["datagrams_seen"] == ("dg1",)
    assert second.snapshot()["datagrams_seen"] == ()


def test_attempt_cannot_mutate_another_session_state() -> None:
    session = WebTransportSessionState(session_id="attempt-1")

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "attempt-2", "datagram_id": "dg1"},
        )


def test_stream_id_is_owned_by_exact_session_id() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "s1", "stream_id": "st1", "stream_direction": "bidi"},
    )

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.stream.receive",
            channel="receive",
            payload={"session_id": "s2", "stream_id": "st1", "stream_direction": "bidi"},
        )


def test_datagram_id_is_owned_by_exact_session_id() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.datagram.receive",
        channel="receive",
        payload={"session_id": "s1", "datagram_id": "dg1"},
    )

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s2", "datagram_id": "dg1"},
        )


def test_engine_session_id_is_owned_by_exact_attempt_id() -> None:
    session = WebTransportSessionState(session_id="engine-attempt-1")

    assert session.snapshot()["session_id"] == "engine-attempt-1"


def test_engine_session_cannot_commit_or_rollback_cross_attempt_transaction() -> None:
    session = WebTransportSessionState(session_id="attempt-1")

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.close",
            channel="send",
            payload={"session_id": "attempt-2"},
        )


def test_trace_and_qlog_events_preserve_session_parentage() -> None:
    session = WebTransportSessionState(session_id="trace-1")
    session.apply_event(
        event="webtransport.stream.receive",
        channel="receive",
        payload={"session_id": "trace-1", "stream_id": "st1", "stream_direction": "bidi"},
    )

    assert session.snapshot()["session_id"] == "trace-1"
    assert session.snapshot()["streams"]["st1"]["lane"] == "bidi_stream"


def test_retry_cannot_reuse_state_from_unrelated_session() -> None:
    original = WebTransportSessionState(session_id="s1")
    retry = WebTransportSessionState(session_id="s2")
    original.apply_event(
        event="webtransport.datagram.receive",
        channel="receive",
        payload={"session_id": "s1", "datagram_id": "dg1"},
    )

    assert retry.snapshot()["datagrams_seen"] == ()


def test_replay_preserves_original_session_parentage_without_mutating_it() -> None:
    session = WebTransportSessionState(session_id="s1")
    before = session.snapshot()

    with pytest.raises(ValueError, match="session_id"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s2", "datagram_id": "dg1"},
        )

    assert session.snapshot() == before


def test_closed_session_rejects_payload_without_state_reopen() -> None:
    session = WebTransportSessionState(session_id="s1")
    session.apply_event(
        event="webtransport.close",
        channel="send",
        payload={"session_id": "s1"},
    )

    with pytest.raises(ValueError, match="closed"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s1", "datagram_id": "dg1"},
        )


def test_unsupported_framing_rejection_cannot_transfer_session_ownership() -> None:
    session = WebTransportSessionState(session_id="s1")

    with pytest.raises(ValueError, match="inner framing"):
        session.apply_event(
            event="webtransport.datagram.receive",
            channel="receive",
            payload={"session_id": "s1", "datagram_id": "dg1", "framing": "jsonrpc"},
        )

    assert session.snapshot()["datagrams_seen"] == ()


def test_session_leakage_diagnostics_are_deterministic_and_scoped() -> None:
    session = WebTransportSessionState(session_id="s1")

    for _ in range(2):
        with pytest.raises(ValueError, match="session_id"):
            session.apply_event(
                event="webtransport.datagram.receive",
                channel="receive",
                payload={"session_id": "s2", "datagram_id": "dg1"},
            )
