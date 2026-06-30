from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any


@dataclass
class _Bucket:
    tokens: float
    t_last: float


class RateLimiter:
    """Token-bucket limiter: allow/reserve by arbitrary key.

    Semantics:
      - rate_per_s: refill rate
      - burst: max tokens
      - cost: tokens consumed per request
      - allow() returns bool
      - reserve() returns wait_s (0 if immediate) or None if impossible (cost > burst)
    """

    def __init__(self, *, rate_per_s: float, burst: float, shards: int = 64, namespace: str = "default") -> None:
        if rate_per_s <= 0:
            raise ValueError("rate_per_s must be > 0")
        if burst <= 0:
            raise ValueError("burst must be > 0")
        if shards <= 0:
            raise ValueError("shards must be > 0")
        self.rate_per_s = float(rate_per_s)
        self.burst = float(burst)
        self.shards = int(shards)
        self.namespace = namespace

        self._locks = [RLock() for _ in range(self.shards)]
        self._maps: list[dict[str, _Bucket]] = [dict() for _ in range(self.shards)]

    def _idx(self, key: str) -> int:
        # deterministic per-process; good enough for sharding
        return (hash((self.namespace, key)) & 0x7FFFFFFF) % self.shards

    def _refill(self, b: _Bucket, now: float) -> None:
        dt = now - b.t_last
        if dt <= 0:
            return
        b.tokens = min(self.burst, b.tokens + dt * self.rate_per_s)
        b.t_last = now

    def _get_bucket(self, m: dict[str, _Bucket], key: str, now: float) -> _Bucket:
        b = m.get(key)
        if b is None:
            b = _Bucket(tokens=self.burst, t_last=now)
            m[key] = b
        return b

    def allow(self, key: str, *, cost: float = 1.0) -> bool:
        wait = self.reserve(key, cost=cost)
        return wait == 0.0

    def reserve(self, key: str, *, cost: float = 1.0) -> float | None:
        """Reserve tokens; returns wait seconds if not immediately available.

        - If cost > burst, returns None (impossible).
        - Otherwise deducts immediately if available; else returns required wait time WITHOUT deducting.
          Caller may sleep and retry, or use wait to schedule.
        """
        if cost <= 0:
            return 0.0
        if cost > self.burst:
            return None

        now = monotonic()
        i = self._idx(key)
        with self._locks[i]:
            m = self._maps[i]
            b = self._get_bucket(m, key, now)
            self._refill(b, now)
            if b.tokens >= cost:
                b.tokens -= cost
                return 0.0
            deficit = cost - b.tokens
            # time until enough tokens accumulate
            wait_s = deficit / self.rate_per_s
            return max(0.0, wait_s)

    def stats(self, key: str) -> dict[str, Any]:
        now = monotonic()
        i = self._idx(key)
        with self._locks[i]:
            m = self._maps[i]
            b = self._get_bucket(m, key, now)
            self._refill(b, now)
            return {
                "key": key,
                "tokens": b.tokens,
                "burst": self.burst,
                "rate_per_s": self.rate_per_s,
            }
