from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest

from tigrbl_runtime.protocol.client_session_coverage import (
    ClientTopology,
    CoverageDisposition,
    build_matrix_row,
)


@dataclass
class InMemorySession:
    client_id: str
    session_id: str
    closed: bool = False
    payloads: list[str] = field(default_factory=list)


class InMemoryTopologyHarness:
    def __init__(self) -> None:
        self.sessions: dict[str, InMemorySession] = {}
        self.events: list[dict[str, Any]] = []

    def open(self, client_id: str, session_id: str, topology: ClientTopology) -> None:
        if session_id in self.sessions and not self.sessions[session_id].closed:
            raise ValueError(f"session already open: {session_id}")
        self.sessions[session_id] = InMemorySession(client_id=client_id, session_id=session_id)
        self.events.append(self._record("open", client_id, session_id, topology))

    def send(
        self,
        client_id: str,
        session_id: str,
        topology: ClientTopology,
        payload: str,
    ) -> None:
        session = self._session_for(client_id, session_id)
        session.payloads.append(payload)
        self.events.append(
            self._record(
                "send",
                client_id,
                session_id,
                topology,
                payload=payload,
            )
        )

    async def send_async(
        self,
        client_id: str,
        session_id: str,
        topology: ClientTopology,
        payload: str,
        delay: float,
    ) -> None:
        await asyncio.sleep(delay)
        self.send(client_id, session_id, topology, payload)

    def close(self, client_id: str, session_id: str, topology: ClientTopology) -> None:
        session = self._session_for(client_id, session_id)
        session.closed = True
        self.events.append(self._record("close", client_id, session_id, topology))

    def _session_for(self, client_id: str, session_id: str) -> InMemorySession:
        session = self.sessions[session_id]
        if session.client_id != client_id:
            raise PermissionError("cross-client session access rejected")
        if session.closed:
            raise RuntimeError("post-close send rejected")
        return session

    @staticmethod
    def _record(
        subevent: str,
        client_id: str,
        session_id: str,
        topology: ClientTopology,
        **extra: Any,
    ) -> dict[str, Any]:
        return build_matrix_row(
            transport_scenario="WebTransport",
            client_topology=topology,
            disposition=CoverageDisposition.COVERED,
            lifecycle_behavior=CoverageDisposition.COVERED,
            isolation_property=CoverageDisposition.COVERED,
            pressure_mode=CoverageDisposition.REQUIRED,
            fault_mode=CoverageDisposition.REQUIRED,
            client_id=client_id,
            session_id=session_id,
            subevent=subevent,
            **extra,
        )


def test_sequential_clients_complete_without_overlap_or_state_leakage() -> None:
    harness = InMemoryTopologyHarness()

    harness.open("client-a", "session-a", ClientTopology.SEQUENTIAL_CLIENTS)
    harness.send("client-a", "session-a", ClientTopology.SEQUENTIAL_CLIENTS, "a-1")
    harness.close("client-a", "session-a", ClientTopology.SEQUENTIAL_CLIENTS)
    harness.open("client-b", "session-b", ClientTopology.SEQUENTIAL_CLIENTS)
    harness.send("client-b", "session-b", ClientTopology.SEQUENTIAL_CLIENTS, "b-1")
    harness.close("client-b", "session-b", ClientTopology.SEQUENTIAL_CLIENTS)

    assert [event["client_id"] for event in harness.events] == [
        "client-a",
        "client-a",
        "client-a",
        "client-b",
        "client-b",
        "client-b",
    ]
    assert harness.sessions["session-a"].payloads == ["a-1"]
    assert harness.sessions["session-b"].payloads == ["b-1"]


def test_bounded_interleaved_clients_preserve_controlled_ordering() -> None:
    harness = InMemoryTopologyHarness()
    topology = ClientTopology.BOUNDED_INTERLEAVED_CLIENTS
    harness.open("client-a", "session-a", topology)
    harness.open("client-b", "session-b", topology)

    for client_id, session_id, payload in [
        ("client-a", "session-a", "a-1"),
        ("client-b", "session-b", "b-1"),
        ("client-a", "session-a", "a-2"),
        ("client-b", "session-b", "b-2"),
    ]:
        harness.send(client_id, session_id, topology, payload)

    send_events = [event for event in harness.events if event["subevent"] == "send"]
    assert [(event["client_id"], event["payload"]) for event in send_events] == [
        ("client-a", "a-1"),
        ("client-b", "b-1"),
        ("client-a", "a-2"),
        ("client-b", "b-2"),
    ]
    assert harness.sessions["session-a"].payloads == ["a-1", "a-2"]
    assert harness.sessions["session-b"].payloads == ["b-1", "b-2"]


@pytest.mark.asyncio
async def test_concurrent_clients_preserve_session_isolation() -> None:
    harness = InMemoryTopologyHarness()
    topology = ClientTopology.CONCURRENT_CLIENTS
    for index in range(6):
        harness.open(f"client-{index}", f"session-{index}", topology)

    await asyncio.gather(
        *[
            harness.send_async(
                f"client-{index}",
                f"session-{index}",
                topology,
                f"payload-{index}",
                delay=0.001 * (index % 3),
            )
            for index in range(6)
        ]
    )

    assert len([event for event in harness.events if event["subevent"] == "send"]) == 6
    for index in range(6):
        assert harness.sessions[f"session-{index}"].payloads == [f"payload-{index}"]


def test_churn_clients_reconnect_without_disrupting_active_clients() -> None:
    harness = InMemoryTopologyHarness()
    topology = ClientTopology.CHURN_CLIENTS

    harness.open("client-a", "session-a-1", topology)
    harness.open("client-b", "session-b", topology)
    harness.send("client-b", "session-b", topology, "b-before")
    harness.close("client-a", "session-a-1", topology)
    harness.open("client-a", "session-a-2", topology)
    harness.send("client-a", "session-a-2", topology, "a-reconnected")
    harness.send("client-b", "session-b", topology, "b-after")

    assert harness.sessions["session-a-1"].closed is True
    assert harness.sessions["session-a-2"].payloads == ["a-reconnected"]
    assert harness.sessions["session-b"].payloads == ["b-before", "b-after"]
    with pytest.raises(RuntimeError, match="post-close"):
        harness.send("client-a", "session-a-1", topology, "late")
