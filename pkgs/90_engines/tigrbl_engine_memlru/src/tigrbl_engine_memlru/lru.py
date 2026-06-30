from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from threading import RLock
from time import monotonic
from typing import Any


@dataclass
class _Entry:
    value: Any
    cost: float
    t: float


class LRUCache:
    """LRU cache with optional cost budget.

    Eviction:
      - Always enforces max_items.
      - If max_cost set, evicts LRU until total_cost <= max_cost.
    """

    def __init__(
        self,
        *,
        max_items: int = 100_000,
        max_cost: float | None = None,
        default_cost: float = 1.0,
        namespace: str = "default",
    ) -> None:
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        if max_cost is not None and max_cost <= 0:
            raise ValueError("max_cost must be > 0 if set")
        if default_cost <= 0:
            raise ValueError("default_cost must be > 0")
        self.max_items = int(max_items)
        self.max_cost = float(max_cost) if max_cost is not None else None
        self.default_cost = float(default_cost)
        self.namespace = namespace

        self._lock = RLock()
        self._od: OrderedDict[str, _Entry] = OrderedDict()
        self._total_cost = 0.0

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            e = self._od.get(key)
            if e is None:
                return default
            self._od.move_to_end(key, last=True)
            return e.value

    def set(self, key: str, value: Any, *, cost: float | None = None) -> None:
        if cost is None:
            cost = self.default_cost
        c = float(cost)
        if c <= 0:
            raise ValueError("cost must be > 0")
        now = monotonic()
        with self._lock:
            old = self._od.pop(key, None)
            if old is not None:
                self._total_cost -= old.cost
            self._od[key] = _Entry(value=value, cost=c, t=now)
            self._od.move_to_end(key, last=True)
            self._total_cost += c
            self._evict()

    def delete(self, key: str) -> bool:
        with self._lock:
            e = self._od.pop(key, None)
            if e is None:
                return False
            self._total_cost -= e.cost
            return True

    def clear(self) -> None:
        with self._lock:
            self._od.clear()
            self._total_cost = 0.0

    def stats(self) -> dict[str, Any]:
        with self._lock:
            return {
                "size": len(self._od),
                "max_items": self.max_items,
                "total_cost": self._total_cost,
                "max_cost": self.max_cost,
                "default_cost": self.default_cost,
            }

    def _evict(self) -> None:
        while len(self._od) > self.max_items:
            k, e = self._od.popitem(last=False)
            self._total_cost -= e.cost
        if self.max_cost is not None:
            while self._total_cost > self.max_cost and self._od:
                k, e = self._od.popitem(last=False)
                self._total_cost -= e.cost
