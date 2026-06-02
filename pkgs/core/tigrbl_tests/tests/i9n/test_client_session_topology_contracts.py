from __future__ import annotations

import asyncio

import pytest

from tigrbl_runtime.protocol.client_session_coverage import (
    ClientTopology,
    ClientSessionTopologyRecorder,
)


def test_sequential_clients_complete_without_overlap_or_state_leakage() -> None:
    harness = ClientSessionTopologyRecorder()

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
    harness = ClientSessionTopologyRecorder()
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
    harness = ClientSessionTopologyRecorder()
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
    harness = ClientSessionTopologyRecorder()
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
