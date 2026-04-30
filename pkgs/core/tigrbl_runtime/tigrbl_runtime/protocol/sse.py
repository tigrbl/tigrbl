from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ._iterators import aclose_if_supported, iter_items

async def run_sse_chain(config: Mapping[str, Any]) -> dict[str, object]:
    producer = config.get("producer")
    send = config.get("send")
    stop_after = config.get("stop_after")
    disconnect_after = config.get("disconnect_after")
    emitted = 0
    subevents = ["session.open", "stream.start"]

    async for event in iter_items(producer):
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
            await aclose_if_supported(producer)
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
    if data is None or isinstance(data, (str, bytes, int, float, bool)):
        return True
    try:
        json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    except TypeError:
        return False
    return True


def _encode_event(event: Mapping[str, Any]) -> bytes:
    name = event.get("event")
    data = event.get("data", "")
    lines: list[str] = []
    if name:
        lines.append(f"event: {name}")
    if isinstance(data, str):
        for part in data.splitlines() or [data]:
            lines.append(f"data: {part}")
    elif isinstance(data, (bytes, bytearray, memoryview)):
        lines.append(f"data: {bytes(data).decode('utf-8')}")
    else:
        lines.append(f"data: {json.dumps(data, separators=(',', ':'), ensure_ascii=False)}")
    return ("\n".join(lines) + "\n\n").encode("utf-8")


__all__ = ["run_sse_chain"]
