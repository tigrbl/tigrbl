from __future__ import annotations

from tigrbl_base._base import EngineSessionBase

from .dedupe import DedupeSet


class DedupeSession(EngineSessionBase):
    def __init__(self, engine: DedupeSet) -> None:
        super().__init__()
        self._engine = engine
        self._closed = False

    async def _tx_begin_impl(self) -> None:
        return

    async def _tx_commit_impl(self) -> None:
        return

    async def _tx_rollback_impl(self) -> None:
        return

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
