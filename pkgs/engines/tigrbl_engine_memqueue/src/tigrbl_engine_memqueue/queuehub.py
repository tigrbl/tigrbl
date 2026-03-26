from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from threading import Condition, RLock
from time import monotonic
from typing import Any


@dataclass
class _Q:
    mode: str
    max_items: int
    lock: RLock
    cv: Condition
    # one of these is used depending on mode
    dq: deque[Any] | None = None
    heap: list[tuple[int, float, Any]] | None = None
    seq: int = 0
    closed: bool = False


class QueueHub:
    """Named in-process queues with blocking get/put.

    Modes:
      - fifo: deque append/pop left
      - lifo: deque append/pop
      - priority: heapq of (priority, t, item) (lower priority value first)
    """

    def __init__(self, *, mode: str = "fifo", max_items: int = 100_000, namespace: str = "default") -> None:
        mode = (mode or "fifo").lower()
        if mode not in {"fifo", "lifo", "priority"}:
            raise ValueError("mode must be fifo|lifo|priority")
        if max_items <= 0:
            raise ValueError("max_items must be > 0")
        self.mode = mode
        self.max_items = int(max_items)
        self.namespace = namespace
        self._lock = RLock()
        self._qs: dict[str, _Q] = {}

    def _q(self, name: str) -> _Q:
        k = name or "default"
        with self._lock:
            q = self._qs.get(k)
            if q is None:
                lock = RLock()
                cv = Condition(lock)
                if self.mode == "priority":
                    q = _Q(mode=self.mode, max_items=self.max_items, lock=lock, cv=cv, heap=[])
                else:
                    q = _Q(mode=self.mode, max_items=self.max_items, lock=lock, cv=cv, dq=deque())
                self._qs[k] = q
            return q

    def close(self, name: str = "default") -> None:
        q = self._q(name)
        with q.lock:
            q.closed = True
            q.cv.notify_all()

    def put(self, name: str, item: Any, *, priority: int = 0, timeout: float | None = None) -> bool:
        q = self._q(name)
        deadline = None if timeout is None else (monotonic() + max(0.0, float(timeout)))
        with q.lock:
            while not q.closed and self.size(name) >= q.max_items:
                if deadline is None:
                    q.cv.wait()
                else:
                    remain = deadline - monotonic()
                    if remain <= 0:
                        return False
                    q.cv.wait(remain)
            if q.closed:
                return False
            if q.mode == "priority":
                assert q.heap is not None
                q.seq += 1
                heapq.heappush(q.heap, (int(priority), monotonic(), item))
            else:
                assert q.dq is not None
                q.dq.append(item)
            q.cv.notify()
            return True

    def get(self, name: str, *, timeout: float | None = None) -> Any | None:
        q = self._q(name)
        deadline = None if timeout is None else (monotonic() + max(0.0, float(timeout)))
        with q.lock:
            while not q.closed and self.size(name) == 0:
                if deadline is None:
                    q.cv.wait()
                else:
                    remain = deadline - monotonic()
                    if remain <= 0:
                        return None
                    q.cv.wait(remain)
            if self.size(name) == 0:
                return None
            if q.mode == "priority":
                assert q.heap is not None
                _pri, _t, item = heapq.heappop(q.heap)
            elif q.mode == "lifo":
                assert q.dq is not None
                item = q.dq.pop()
            else:  # fifo
                assert q.dq is not None
                item = q.dq.popleft()
            q.cv.notify()
            return item

    def drain(self, name: str, *, max_items: int | None = None) -> list[Any]:
        q = self._q(name)
        out: list[Any] = []
        with q.lock:
            n = self.size(name)
            if max_items is not None:
                n = min(n, int(max_items))
            for _ in range(n):
                item = self.get(name, timeout=0.0)
                if item is None:
                    break
                out.append(item)
            return out

    def size(self, name: str) -> int:
        q = self._q(name)
        if q.mode == "priority":
            assert q.heap is not None
            return len(q.heap)
        assert q.dq is not None
        return len(q.dq)
