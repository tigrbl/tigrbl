from __future__ import annotations

import json
import struct

import pytest

from tigrbl_ops_realtime.sinks import RealtimeEnvelope, WebTransportRealtimeSink


@pytest.mark.asyncio
async def test_realtime_notifications_reuse_one_nonterminal_server_stream() -> None:
    emitted: list[dict[str, object]] = []

    async def send(message: dict[str, object]) -> None:
        emitted.append(message)

    sink = WebTransportRealtimeSink(send, session_id="session-1")
    await sink.send_realtime(RealtimeEnvelope("room:one", {"sequence": 1}))
    await sink.send_realtime(RealtimeEnvelope("room:one", {"sequence": 2}))

    assert [item["stream_id"] for item in emitted] == [
        "realtime-events",
        "realtime-events",
    ]
    assert [item["more"] for item in emitted] == [True, True]
    decoded = []
    for item in emitted:
        data = item["data"]
        assert isinstance(data, bytes)
        size = struct.unpack("!I", data[:4])[0]
        decoded.append(json.loads(data[4 : 4 + size]))
    assert [item["params"]["event"]["sequence"] for item in decoded] == [1, 2]
    assert all(item["params"]["publication_id"].startswith("pub_") for item in decoded)
    assert all(item["params"]["notification_id"].startswith("ntf_") for item in decoded)
    assert all("id" not in item for item in decoded)
