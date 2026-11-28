from __future__ import annotations

import json

import pytest

from tigrbl_atoms.atoms.framing import encode_jsonrpc_record
from tigrbl_kernel.webtransport_session_plan import WebTransportSessionPlan


def test_session_plan_decodes_fragmented_and_coalesced_control_records() -> None:
    plan = WebTransportSessionPlan()
    first = {"jsonrpc": "2.0", "id": "1", "method": "Room.join"}
    second = {"jsonrpc": "2.0", "id": "2", "method": "Chat.submit"}
    payload = encode_jsonrpc_record(first) + encode_jsonrpc_record(second)
    base = {
        "type": "webtransport.stream.receive",
        "session_id": "session-1",
        "stream_id": 0,
        "stream_direction": "bidi",
        "stream_initiator": "client",
    }

    plan.project_receive({**base, "data": payload[:2], "more": True})
    assert not plan.has_pending()
    plan.project_receive({**base, "data": payload[2:7], "more": True})
    assert not plan.has_pending()
    plan.project_receive({**base, "data": payload[7:], "more": True})

    first_event = plan.pop_pending()
    second_event = plan.pop_pending()
    assert json.loads(first_event["data"]) == first
    assert json.loads(second_event["data"]) == second
    assert first_event["stream_id"] == second_event["stream_id"] == 0
    assert first_event["more"] is True
    assert second_event["more"] is True
    assert first_event["jsonrpc_complete"] is True
    assert second_event["jsonrpc_complete"] is True
    assert not plan.has_pending()


def test_session_plan_releases_only_the_terminated_stream_decoder() -> None:
    plan = WebTransportSessionPlan()
    record = encode_jsonrpc_record({"jsonrpc": "2.0", "id": 1, "method": "Room.join"})
    base = {
        "type": "webtransport.stream.receive",
        "stream_direction": "bidi",
        "more": True,
    }
    for stream in ("closing", "active"):
        plan.project_receive({**base, "stream_id": stream, "data": record[:2]})
    assert not plan.has_pending()

    close = {"type": "webtransport.stream.reset", "stream_id": "closing"}
    plan.project_receive(close)
    assert plan.pop_pending() == close
    assert set(plan.control_decoders) == {"active"}
    plan.project_receive({**base, "stream_id": "active", "data": record[2:]})
    assert json.loads(plan.pop_pending()["data"])["id"] == 1


@pytest.mark.asyncio
async def test_eager_drain_propagates_the_carrier_timeout():
    plan = WebTransportSessionPlan()
    event = {"type": "webtransport.datagram.receive", "datagram_id": "d1"}
    failure = TimeoutError("carrier receive failed")
    recorded = []

    async def receive():
        if not recorded:
            return event
        raise failure

    async def record(message):
        recorded.append(message)

    with pytest.raises(TimeoutError) as caught:
        await plan.receive_unit(receive, record, eager_drain=True)

    assert caught.value is failure
    assert recorded == [event]
