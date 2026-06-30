from __future__ import annotations

import heapq
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any


@dataclass(order=True)
class _Exp:
    expires_at: float
    key: str


class DedupeSet:
    """Exact TTL membership set with bounded size.

    Stores: key -> expires_at (monotonic seconds)
    Cleanup: min-heap of expirations for amortized O(log n) eviction.
    """

    def __init__(self, *, default_ttl_s: float = 60.0, max_items: int = 1_000_000, namespace: str = "default") -> None:
        if default_ttl_s <= 0:
            raise ValueError("default_ttl_s must be > 0")
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        self.default_ttl_s = float(default_ttl_s)
        self.max_items = int(max_items)
        self.namespace = namespace

        self._lock = RLock()
        self._m: dict[str, float] = {}
        self._h: list[_Exp] = []

    def _gc(self, now: float) -> None:
        # Pop until heap head is not expired or stale.
        while self._h:
            exp = self._h[0]
            if exp.expires_at > now:
                return
            heapq.heappop(self._h)
            cur = self._m.get(exp.key)
            if cur is None:
                continue
            if cur <= now:
                self._m.pop(exp.key, None)

    def seen(self, key: str) -> bool:
        now = monotonic()
        with self._lock:
            self._gc(now)
            exp = self._m.get(key)
            return exp is not None and exp > now

    def mark(self, key: str, *, ttl_s: float | None = None) -> None:
        now = monotonic()
        ttl = self.default_ttl_s if ttl_s is None else float(ttl_s)
        if ttl <= 0:
            raise ValueError("ttl_s must be > 0")
        exp_at = now + ttl
        with self._lock:
            self._gc(now)
            self._m[key] = exp_at
            heapq.heappush(self._h, _Exp(exp_at, key))
            self._enforce_max(now)

    def mark_if_absent(self, key: str, *, ttl_s: float | None = None) -> bool:
        now = monotonic()
        ttl = self.default_ttl_s if ttl_s is None else float(ttl_s)
        if ttl <= 0:
            raise ValueError("ttl_s must be > 0")
        exp_at = now + ttl
        with self._lock:
            self._gc(now)
            cur = self._m.get(key)
            if cur is not None and cur > now:
                return False
            self._m[key] = exp_at
            heapq.heappush(self._h, _Exp(exp_at, key))
            self._enforce_max(now)
            return True

    def delete(self, key: str) -> bool:
        now = monotonic()
        with self._lock:
            self._gc(now)
            return self._m.pop(key, None) is not None

    def size(self) -> int:
        now = monotonic()
        with self._lock:
            self._gc(now)
            return len(self._m)

    def reset(self) -> None:
        with self._lock:
            self._m.clear()
            self._h.clear()

    def stats(self) -> dict[str, Any]:
        now = monotonic()
        with self._lock:
            self._gc(now)
            return {"size": len(self._m), "max_items": self.max_items, "default_ttl_s": self.default_ttl_s}

    def _enforce_max(self, now: float) -> None:
        # If above max, evict oldest-expiring keys (heap order)
        while len(self._m) > self.max_items and self._h:
            exp = heapq.heappop(self._h)
            cur = self._m.get(exp.key)
            if cur is None:
                continue
            # evict regardless of expiration order; this is a hard cap
            self._m.pop(exp.key, None)
