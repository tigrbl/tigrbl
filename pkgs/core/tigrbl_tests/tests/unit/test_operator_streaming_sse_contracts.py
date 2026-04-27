from __future__ import annotations

from typing import Any

import pytest

from tigrbl_concrete._concrete._event_stream_response import EventStreamResponse
from tigrbl_concrete._concrete._streaming_response import StreamingResponse


async def _collect_response_messages(response: Any) -> list[dict[str, Any]]:
    sent: list[dict[str, Any]] = []

    async def send(message: dict[str, Any]) -> None:
        sent.append(message)

    await response(
        {"type": "http", "method": "GET", "path": "/", "headers": []},
        lambda: {"type": "http.request", "body": b"", "more_body": False},
        send,
    )
    return sent


@pytest.mark.asyncio
async def test_streaming_response_accepts_async_iterables_and_preserves_chunk_order() -> None:
    async def chunks():
        yield b"first"
        yield b"second"

    response = StreamingResponse(chunks(), media_type="text/plain", status_code=202)
    messages = await _collect_response_messages(response)

    start = messages[0]
    bodies = [message for message in messages if message["type"] == "http.response.body"]

    assert start["status"] == 202
    assert dict(start["headers"])[b"content-type"] == b"text/plain"
    assert [body["body"] for body in bodies] == [b"first", b"second", b""]
    assert [body["more_body"] for body in bodies] == [True, True, False]


@pytest.mark.asyncio
async def test_streaming_response_treats_bytes_as_a_single_chunk() -> None:
    response = StreamingResponse(b"single-body", media_type="application/octet-stream")
    messages = await _collect_response_messages(response)
    bodies = [message for message in messages if message["type"] == "http.response.body"]

    assert [body["body"] for body in bodies] == [b"single-body", b""]
    assert bodies[-1]["more_body"] is False


@pytest.mark.asyncio
async def test_sse_response_encodes_event_id_retry_multiline_data_and_heartbeats() -> None:
    response = EventStreamResponse(
        [
            {"event": "notice", "id": "evt-1", "retry": 5000, "data": "one\ntwo"},
            b": heartbeat\n\n",
        ]
    )
    messages = await _collect_response_messages(response)
    start = messages[0]
    bodies = [message["body"] for message in messages if message["type"] == "http.response.body"]

    assert dict(start["headers"])[b"content-type"].startswith(b"text/event-stream")
    assert dict(start["headers"])[b"cache-control"] == b"no-cache"
    assert bodies[0] == (
        b"event: notice\n"
        b"id: evt-1\n"
        b"retry: 5000\n"
        b"data: one\n"
        b"data: two\n\n"
    )
    assert bodies[1] == b": heartbeat\n\n"
    assert bodies[-1] == b""


@pytest.mark.asyncio
async def test_sse_response_encodes_dict_data_as_compact_json() -> None:
    response = EventStreamResponse([{"data": {"ok": True, "count": 2}}])
    messages = await _collect_response_messages(response)
    body = next(message["body"] for message in messages if message["type"] == "http.response.body")

    assert body == b'data: {"ok":true,"count":2}\n\n'
