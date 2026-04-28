from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class TaskQueueAdapter:
    """Abstract queue adapter. Runtime should provide a concrete instance in ctx."""

    async def enqueue(self, item: dict, *, timeout: Optional[float] = None) -> None:
        raise NotImplementedError

    async def dequeue(self, *, timeout: Optional[float] = None) -> Optional[dict]:
        raise NotImplementedError


class QueueClosedError(RuntimeError):
    """Raised when producers or consumers use a closed queue."""


class InMemoryAsyncQueue(TaskQueueAdapter):
    def __init__(self, *, max_items: int = 1000) -> None:
        if max_items < 1:
            raise ValueError("max_items must be >= 1")
        self._q: asyncio.Queue[dict] = asyncio.Queue(maxsize=max_items)
        self._closed = False

    @property
    def max_items(self) -> int:
        return self._q.maxsize

    @property
    def size(self) -> int:
        return self._q.qsize()

    @property
    def closed(self) -> bool:
        return self._closed

    async def enqueue(self, item: dict, *, timeout: Optional[float] = None) -> None:
        if self._closed:
            raise QueueClosedError("queue is closed")
        if timeout is None:
            await self._q.put(item)
            return
        await asyncio.wait_for(self._q.put(item), timeout=timeout)

    async def dequeue(self, *, timeout: Optional[float] = None) -> Optional[dict]:
        if self._closed and self._q.empty():
            return None
        try:
            if timeout is None:
                return await self._q.get()
            return await asyncio.wait_for(self._q.get(), timeout=timeout)
        except asyncio.TimeoutError:
            return None

    def close(self) -> None:
        self._closed = True


def from_ctx(ctx) -> TaskQueueAdapter:
    ctx = ctx or {}
    q = ctx.get("task_queue")
    if q:
        return q
    return InMemoryAsyncQueue(
        max_items=int((ctx.get("config") or {}).get("acme.task_queue_max_items", 1000))
    )
