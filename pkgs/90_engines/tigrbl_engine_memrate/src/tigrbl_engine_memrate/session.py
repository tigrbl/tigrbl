from __future__ import annotations

from .rate import RateLimiter


class RateSession:
    def __init__(self, engine: RateLimiter) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def allow(self, key: str, *, cost: float = 1.0) -> bool:
        self._require_open()
        return self._engine.allow(key, cost=cost)

    def reserve(self, key: str, *, cost: float = 1.0) -> float | None:
        self._require_open()
        return self._engine.reserve(key, cost=cost)

    def stats(self, key: str) -> dict:
        self._require_open()
        return self._engine.stats(key)

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncRateSession(RateSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
