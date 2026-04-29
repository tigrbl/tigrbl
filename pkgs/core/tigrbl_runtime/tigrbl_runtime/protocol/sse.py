from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Mapping
from typing import Any


async def run_sse_chain(config: Mapping[str, Any]) -> dict[str, object]:
    producer = config.get("producer")
    send = config.get("send")
    stop_after = config.get("stop_after")
    disconnect_after = config.get("disconnect_after")
    emitted = 0
    subevents = ["session.open", "stream.start"]

    async for event in _aiter(producer):
        if not isinstance(event, Mapping) or not _serializable_event(event):
            raise TypeError("SSE event data must be serializable")
        payload = _encode_event(event)
        if callable(send):
            send({"type": "http.response.body", "body": payload, "more_body": True})
        emitted += 1
        subevents.append("message.emit")
        if stop_after is not None and emitted >= int(stop_after):
            return {"lazy": True, "subevents": subevents, "completion_fence": "POST_EMIT"}
        if disconnect_after is not None and emitted >= int(disconnect_after):
            await _aclose(producer)
            subevents.extend(("stream.end", "session.close"))
            return {
                "lazy": True,
                "exit_reason": "disconnect",
                "subevents": subevents,
                "completion_fence": "POST_EMIT",
            }

    subevents.extend(("stream.end", "session.close"))
    return {
        "lazy": True,
        "exit_reason": "producer.exhausted",
        "subevents": subevents,
        "completion_fence": "POST_EMIT",
    }


def _serializable_event(event: Mapping[str, Any]) -> bool:
    data = event.get("data")
    return data is None or isinstance(data, (str, bytes, int, float, bool))


def _encode_event(event: Mapping[str, Any]) -> bytes:
    name = event.get("event")
    data = event.get("data", "")
    lines: list[str] = []
    if name:
        lines.append(f"event: {name}")
    lines.append(f"data: {data}")
    return ("\n".join(lines) + "\n\n").encode("utf-8")


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


__all__ = ["run_sse_chain"]
