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

    assert json.loads(plan.pop_pending()["data"]) == first
    assert json.loads(plan.pop_pending()["data"]) == second
    assert not plan.has_pending()
