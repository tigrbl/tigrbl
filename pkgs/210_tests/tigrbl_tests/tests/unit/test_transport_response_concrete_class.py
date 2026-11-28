from __future__ import annotations

import pytest

from tigrbl import TransportResponse


@pytest.mark.asyncio
async def test_transport_response_is_a_distinct_concrete_response_surface() -> None:
    sent: list[dict[str, object]] = []

    async def _send(message: dict[str, object]) -> None:
        sent.append(message)

    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    response = TransportResponse(
        status_code=200,
        headers={"content-type": "text/plain", "content-length": "999"},
        body=b"hello",
    )

    await response(
        {"type": "http", "method": "GET", "path": "/", "headers": []},
        _receive,
        _send,
    )

    assert type(response).__name__ == "TransportResponse"
    assert isinstance(response, TransportResponse)
    assert sent[0]["status"] == 200
    assert dict(sent[0]["headers"])[b"content-length"] == b"5"
    assert sent[1] == {"type": "http.response.body", "body": b"hello", "more_body": False}


@pytest.mark.asyncio
async def test_transport_response_strips_body_and_entity_headers_for_head() -> None:
    sent: list[dict[str, object]] = []

    async def _send(message: dict[str, object]) -> None:
        sent.append(message)

    async def _receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    response = TransportResponse(
        status_code=200,
        headers={"content-type": "text/plain", "content-length": "999"},
        body=b"hello",
    )

    await response(
        {"type": "http", "method": "HEAD", "path": "/", "headers": []},
        _receive,
        _send,
    )

    headers = dict(sent[0]["headers"])
    assert b"content-length" not in headers
    assert b"content-type" not in headers
    assert sent[1] == {"type": "http.response.body", "body": b"", "more_body": False}
