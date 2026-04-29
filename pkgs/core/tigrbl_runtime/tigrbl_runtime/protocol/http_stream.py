from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Mapping
from typing import Any


async def run_http_stream_chain(config: Mapping[str, Any]) -> dict[str, object]:
    producer = config.get("producer")
    send = config.get("send")
    disconnect_after = config.get("disconnect_after")
    chunks_emitted = 0

    if callable(send):
        send({"type": "http.response.start", "status": 200, "headers": []})

    try:
        async for chunk in _aiter(producer):
            if not isinstance(chunk, (bytes, bytearray, str)):
                raise TypeError("stream chunk must be bytes or str")
            body = chunk.encode("utf-8") if isinstance(chunk, str) else bytes(chunk)
            if callable(send):
                send({"type": "http.response.body", "body": body, "more_body": True})
            chunks_emitted += 1
            if disconnect_after is not None and chunks_emitted >= int(disconnect_after):
                await _aclose(producer)
                return {
                    "exit_reason": "disconnect",
                    "chunks_emitted": chunks_emitted,
                    "completion_fence": "POST_EMIT",
                }
    finally:
        if disconnect_after is not None and chunks_emitted >= int(disconnect_after):
            await _aclose(producer)

    if callable(send):
        send({"type": "http.response.body", "body": b"", "more_body": False})
    return {
        "exit_reason": "producer.exhausted",
        "chunks_emitted": chunks_emitted,
        "completion_fence": "POST_EMIT",
    }


async def _aiter(producer: object) -> AsyncIterator[object]:
    if hasattr(producer, "__aiter__"):
        async for item in producer:  # type: ignore[union-attr]
            yield item
        return
    if isinstance(producer, Iterable):
        for item in producer:
            yield item


async def _aclose(producer: object) -> None:
    close = getattr(producer, "aclose", None)
    if callable(close):
        await close()


__all__ = ["run_http_stream_chain"]
