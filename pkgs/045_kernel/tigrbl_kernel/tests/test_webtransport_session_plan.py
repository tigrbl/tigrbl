from __future__ import annotations

import json

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

    plan.project_receive({**base, "data": payload[:7], "more": True})
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
