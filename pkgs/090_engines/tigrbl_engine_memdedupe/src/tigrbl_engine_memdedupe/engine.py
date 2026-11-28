from __future__ import annotations

from typing import Any

from tigrbl_base._base import EngineBase

from .dedupe import DedupeSet


class DedupeEngine(EngineBase):
    """Tigrbl engine facade over the process-local exact TTL set."""

    def __init__(self, store: DedupeSet, *, spec: Any = None) -> None:
        self.store = store
        self.spec = spec

    def to_provider(self) -> "DedupeEngine":
        return self

    def seen(self, key: str) -> bool:
        return self.store.seen(key)

    def mark(self, key: str, *, ttl_s: float | None = None) -> None:
        self.store.mark(key, ttl_s=ttl_s)

    def mark_if_absent(self, key: str, *, ttl_s: float | None = None) -> bool:
        return self.store.mark_if_absent(key, ttl_s=ttl_s)

    def discard(self, key: str) -> bool:
        return self.store.discard(key)

    def size(self) -> int:
        return self.store.size()

    def reset(self) -> None:
        self.store.reset()

    def stats(self) -> dict[str, Any]:
        return self.store.stats()

    async def _executeloop_impl(self, statements: Any) -> Any:
        del statements
        raise TypeError("memdedupe engines do not execute statement batches")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        del stmt, parameter_sets
        raise TypeError("memdedupe engines do not execute statement batches")


__all__ = ["DedupeEngine"]
