from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Mapping
from typing import Any


async def execute_loop_region(region: Mapping[str, Any]) -> dict[str, object]:
    producer = region.get("producer")
    break_on = region.get("break_on")
    items: list[object] = []
    closed = False

    try:
        async for item in _aiter(producer):
            if item == break_on:
                closed = True
                return {"items": items, "exit_reason": "break", "closed": True}
            items.append(item)
    except Exception as exc:
        return {
            "items": items,
            "exit_reason": "error",
            "closed": True,
            "error_ctx": {
                "loop_id": region.get("loop_id"),
                "role": region.get("role"),
                "subevent": region.get("subevent"),
                "message": str(exc),
                "retry_or_disconnect": "error",
            },
        }

    return {"items": items, "exit_reason": "producer.exhausted", "closed": closed}


async def _aiter(producer: object) -> AsyncIterator[object]:
    if hasattr(producer, "__aiter__"):
        async for item in producer:  # type: ignore[union-attr]
            yield item
        return
    if isinstance(producer, Iterable):
        for item in producer:
            yield item


__all__ = ["execute_loop_region"]
