"""Server-sent events response primitive."""

from __future__ import annotations

import json
from collections.abc import AsyncIterable, Iterable
from typing import Any

from ._streaming_response import StreamingResponse


def _encode_sse_event(event: Any) -> bytes:
    if isinstance(event, (bytes, bytearray, memoryview)):
        payload = bytes(event)
        return payload if payload.endswith(b"\n\n") else payload + b"\n\n"
    if isinstance(event, str):
        return f"data: {event}\n\n".encode("utf-8")
    if isinstance(event, dict):
        lines: list[str] = []
        event_name = event.get("event")
        if event_name is not None:
            lines.append(f"event: {event_name}")
        event_id = event.get("id")
        if event_id is not None:
            lines.append(f"id: {event_id}")
        retry = event.get("retry")
        if retry is not None:
            lines.append(f"retry: {retry}")
        data = event.get("data")
        if data is None:
            lines.append("data:")
        elif isinstance(data, str):
            for part in data.splitlines() or [data]:
                lines.append(f"data: {part}")
        else:
            dumped = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
            lines.append(f"data: {dumped}")
        return ("\n".join(lines) + "\n\n").encode("utf-8")
    dumped = json.dumps(event, separators=(",", ":"), ensure_ascii=False)
    return f"data: {dumped}\n\n".encode("utf-8")


class EventStreamResponse(StreamingResponse):
    def __init__(
        self,
        events: Iterable[Any] | AsyncIterable[Any],
        status_code: int = 200,
        headers: dict[str, str] | list[tuple[str, str]] | None = None,
    ) -> None:
        merged_headers = [
            ("content-type", "text/event-stream; charset=utf-8"),
            ("cache-control", "no-cache"),
        ]
        if headers:
            if hasattr(headers, "items"):
                merged_headers.extend((str(k).lower(), str(v)) for k, v in headers.items())
            else:
                merged_headers.extend((str(k).lower(), str(v)) for k, v in headers)
        if hasattr(events, "__aiter__"):

            async def _aiter():
                async for item in events:  # type: ignore[union-attr]
                    yield _encode_sse_event(item)

            content = _aiter()
        else:
            content = [_encode_sse_event(item) for item in events]
        super().__init__(
            content,
            status_code=status_code,
            media_type="text/event-stream",
            headers=merged_headers,
        )


__all__ = ["EventStreamResponse"]
