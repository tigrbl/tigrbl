from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from tigrbl_runtime.protocol.client_session_coverage import (
    ClientTopology,
    CoverageDisposition,
    build_matrix_row,
)


@dataclass
class RobustSession:
    client_id: str
    session_id: str
    queue_limit: int = 2
    closed: bool = False
    payloads: list[str] = field(default_factory=list)


class RobustHarness:
    def __init__(self) -> None:
        self.sessions: dict[str, RobustSession] = {}
        self.errors: list[dict[str, object]] = []

    def open(self, client_id: str, session_id: str) -> None:
        self.sessions[session_id] = RobustSession(client_id=client_id, session_id=session_id)

    def close(self, client_id: str, session_id: str) -> None:
        self._owned_session(client_id, session_id).closed = True

    def send(
        self,
        client_id: str,
        session_id: str,
        payload: object,
        *,
        framing: str = "json",
    ) -> None:
        session = self._owned_session(client_id, session_id)
        if session.closed:
            self._error(client_id, session_id, "post_close_send")
            raise RuntimeError("post-close send rejected")
        if framing not in {"json", "text", "bytes"}:
            self._error(client_id, session_id, "unsupported_framing")
            raise ValueError("unsupported framing rejected fail-closed")
        if not isinstance(payload, str) or not payload:
            self._error(client_id, session_id, "malformed_payload")
            raise ValueError("malformed payload rejected")
        if len(session.payloads) >= session.queue_limit:
            self._error(client_id, session_id, "pressure_budget_exceeded")
            raise BufferError("bounded queue pressure rejected")
        session.payloads.append(payload)

    def cancel(self, client_id: str, session_id: str) -> None:
        session = self._owned_session(client_id, session_id)
        session.closed = True
        self._error(client_id, session_id, "cancelled")

    def timeout(self, client_id: str, session_id: str) -> None:
        session = self._owned_session(client_id, session_id)
        session.closed = True
        self._error(client_id, session_id, "timeout")

    def _owned_session(self, client_id: str, session_id: str) -> RobustSession:
        session = self.sessions[session_id]
        if session.client_id != client_id:
            self._error(client_id, session_id, "cross_client_session_access")
            raise PermissionError("cross-client session access rejected")
        return session

    def _error(self, client_id: str, session_id: str, error_kind: str) -> None:
        self.errors.append(
            build_matrix_row(
                transport_scenario="WebTransport",
                client_topology=ClientTopology.CONCURRENT_CLIENTS,
                disposition=CoverageDisposition.FAIL_CLOSED,
                lifecycle_behavior=CoverageDisposition.COVERED,
                isolation_property=CoverageDisposition.COVERED,
                pressure_mode=CoverageDisposition.COVERED,
                fault_mode=CoverageDisposition.COVERED,
                client_id=client_id,
                session_id=session_id,
                error_kind=error_kind,
            )
        )


def test_slow_consumer_fast_producer_pressure_is_bounded() -> None:
    harness = RobustHarness()
    harness.open("client-a", "session-a")
    harness.send("client-a", "session-a", "one")
    harness.send("client-a", "session-a", "two")

    with pytest.raises(BufferError, match="bounded queue"):
        harness.send("client-a", "session-a", "three")

    assert harness.sessions["session-a"].payloads == ["one", "two"]
    assert harness.errors[-1]["error_kind"] == "pressure_budget_exceeded"


def test_malformed_payload_and_unsupported_framing_fail_closed() -> None:
    harness = RobustHarness()
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
    harness = RobustHarness()
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
    harness = RobustHarness()
    harness.open("client-a", "session-a")
    harness.open("client-b", "session-b")

    with pytest.raises(PermissionError, match="cross-client"):
        harness.send("client-a", "session-b", "stolen")

    assert harness.sessions["session-a"].payloads == []
    assert harness.sessions["session-b"].payloads == []
    assert harness.errors[-1]["error_kind"] == "cross_client_session_access"
