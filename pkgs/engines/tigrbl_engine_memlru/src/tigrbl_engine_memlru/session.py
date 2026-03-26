from __future__ import annotations

from typing import Any

from .lru import LRUCache


class LRUSession:
    def __init__(self, engine: LRUCache) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def get(self, key: str, default: Any = None) -> Any:
        self._require_open()
        return self._engine.get(key, default)

    def set(self, key: str, value: Any, *, cost: float | None = None) -> None:
        self._require_open()
        self._engine.set(key, value, cost=cost)

    def delete(self, key: str) -> bool:
        self._require_open()
        return self._engine.delete(key)

    def clear(self) -> None:
        self._require_open()
        self._engine.clear()

    def stats(self) -> dict:
        self._require_open()
        return self._engine.stats()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncLRUSession(LRUSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
