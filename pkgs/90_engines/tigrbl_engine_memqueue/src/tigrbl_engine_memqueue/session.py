from __future__ import annotations

from typing import Any

from .queuehub import QueueHub


class QueueSession:
    def __init__(self, engine: QueueHub) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def put(self, item: Any, *, name: str = "default", priority: int = 0, timeout: float | None = None) -> bool:
        self._require_open()
        return self._engine.put(name, item, priority=priority, timeout=timeout)

    def get(self, *, name: str = "default", timeout: float | None = None) -> Any | None:
        self._require_open()
        return self._engine.get(name, timeout=timeout)

    def drain(self, *, name: str = "default", max_items: int | None = None) -> list[Any]:
        self._require_open()
        return self._engine.drain(name, max_items=max_items)

    def qsize(self, *, name: str = "default") -> int:
        self._require_open()
        return self._engine.size(name)

    def close_queue(self, *, name: str = "default") -> None:
        self._require_open()
        self._engine.close(name)

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncQueueSession(QueueSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
