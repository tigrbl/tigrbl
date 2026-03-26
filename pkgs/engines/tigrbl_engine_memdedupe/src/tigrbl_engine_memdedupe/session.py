from __future__ import annotations

from .dedupe import DedupeSet


class DedupeSession:
    def __init__(self, engine: DedupeSet) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def seen(self, key: str) -> bool:
        self._require_open()
        return self._engine.seen(key)

    def mark(self, key: str, *, ttl_s: float | None = None) -> None:
        self._require_open()
        self._engine.mark(key, ttl_s=ttl_s)

    def mark_if_absent(self, key: str, *, ttl_s: float | None = None) -> bool:
        self._require_open()
        return self._engine.mark_if_absent(key, ttl_s=ttl_s)

    def delete(self, key: str) -> bool:
        self._require_open()
        return self._engine.delete(key)

    def size(self) -> int:
        self._require_open()
        return self._engine.size()

    def reset(self) -> None:
        self._require_open()
        self._engine.reset()

    def stats(self) -> dict:
        self._require_open()
        return self._engine.stats()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncDedupeSession(DedupeSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
