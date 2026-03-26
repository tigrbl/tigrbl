from __future__ import annotations

import heapq
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any, Iterable


@dataclass(order=True)
class _Exp:
    expires_at: float
    key: str
    version: int


@dataclass
class _Val:
    version: int
    value: Any
    expires_at: float | None


class KVStore:
    """Versioned in-memory KV with TTL and CAS.

    Keyspace is namespaced at engine level.
    TTL uses monotonic clock; cleanup is heap-based and amortized.
    """

    def __init__(self, *, namespace: str = "default", default_ttl_s: float | None = None, max_items: int = 1_000_000) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        if default_ttl_s is not None and default_ttl_s <= 0:
            raise ValueError("default_ttl_s must be > 0 if set")
        self.namespace = namespace
        self.default_ttl_s = default_ttl_s
        self.max_items = int(max_items)

        self._lock = RLock()
        self._m: dict[str, _Val] = {}
        self._h: list[_Exp] = []

    def _gc(self, now: float) -> None:
        while self._h:
            e = self._h[0]
            if e.expires_at > now:
                return
            heapq.heappop(self._h)
            cur = self._m.get(e.key)
            if cur is None:
                continue
            # only evict if version matches and is actually expired
            if cur.version == e.version and cur.expires_at is not None and cur.expires_at <= now:
                self._m.pop(e.key, None)

    def _set(self, key: str, value: Any, ttl_s: float | None) -> int:
        now = monotonic()
        with self._lock:
            self._gc(now)
            cur = self._m.get(key)
            ver = 1 if cur is None else (cur.version + 1)
            exp_at: float | None = None
            if ttl_s is None:
                ttl_s = self.default_ttl_s
            if ttl_s is not None:
                ttl = float(ttl_s)
                if ttl <= 0:
                    raise ValueError("ttl_s must be > 0 if set")
                exp_at = now + ttl
            self._m[key] = _Val(version=ver, value=value, expires_at=exp_at)
            if exp_at is not None:
                heapq.heappush(self._h, _Exp(exp_at, key, ver))
            self._enforce_max(now)
            return ver

    def get(self, key: str, default: Any = None) -> Any:
        now = monotonic()
        with self._lock:
            self._gc(now)
            v = self._m.get(key)
            if v is None:
                return default
            if v.expires_at is not None and v.expires_at <= now:
                self._m.pop(key, None)
                return default
            return v.value

    def get_version(self, key: str) -> int | None:
        now = monotonic()
        with self._lock:
            self._gc(now)
            v = self._m.get(key)
            if v is None:
                return None
            if v.expires_at is not None and v.expires_at <= now:
                self._m.pop(key, None)
                return None
            return v.version

    def set(self, key: str, value: Any, *, ttl_s: float | None = None) -> int:
        return self._set(key, value, ttl_s)

    def cas(self, key: str, expected_version: int, value: Any, *, ttl_s: float | None = None) -> int | None:
        now = monotonic()
        with self._lock:
            self._gc(now)
            cur = self._m.get(key)
            if cur is None:
                return None
            if cur.expires_at is not None and cur.expires_at <= now:
                self._m.pop(key, None)
                return None
            if cur.version != int(expected_version):
                return None
        # perform write outside of read lock? keep simple: do within lock
        with self._lock:
            self._gc(monotonic())
            cur2 = self._m.get(key)
            if cur2 is None or cur2.version != int(expected_version):
                return None
            return self._set(key, value, ttl_s)

    def delete(self, key: str) -> bool:
        now = monotonic()
        with self._lock:
            self._gc(now)
            return self._m.pop(key, None) is not None

    def keys(self, prefix: str = "") -> list[str]:
        now = monotonic()
        with self._lock:
            self._gc(now)
            if not prefix:
                return sorted(self._m.keys())
            return sorted(k for k in self._m.keys() if k.startswith(prefix))

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
        # Evict arbitrary oldest-expiring entries to enforce cap
        while len(self._m) > self.max_items and self._h:
            e = heapq.heappop(self._h)
            self._m.pop(e.key, None)
