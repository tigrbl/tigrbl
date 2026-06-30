from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from threading import Condition, RLock
from time import monotonic
from typing import Any


@dataclass
class _Sub:
    lock: RLock
    cv: Condition
    dq: deque[Any]
    closed: bool = False


class Subscription:
    def __init__(self, hub: "PubSubHub", topic: str, sub: _Sub) -> None:
        self._hub = hub
        self._topic = topic
        self._sub = sub
        self._closed = False

    def recv(self, timeout: float | None = None) -> Any | None:
        if self._closed:
            return None
        deadline = None if timeout is None else (monotonic() + max(0.0, float(timeout)))
        s = self._sub
        with s.lock:
            while not s.closed and not s.dq:
                if deadline is None:
                    s.cv.wait()
                else:
                    remain = deadline - monotonic()
                    if remain <= 0:
                        return None
                    s.cv.wait(remain)
            if not s.dq:
                return None
            return s.dq.popleft()

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._hub._unsubscribe(self._topic, self._sub)

    @property
    def topic(self) -> str:
        return self._topic


class PubSubHub:
    """In-process pub/sub with fanout to per-subscriber queues."""

    def __init__(self, *, max_backlog_per_sub: int = 1024, drop_policy: str = "drop_old", namespace: str = "default") -> None:
        if max_backlog_per_sub <= 0:
            raise ValueError("max_backlog_per_sub must be > 0")
        drop_policy = (drop_policy or "drop_old").lower()
        if drop_policy not in {"drop_old", "drop_new", "block"}:
            raise ValueError("drop_policy must be drop_old|drop_new|block")
        self.max_backlog_per_sub = int(max_backlog_per_sub)
        self.drop_policy = drop_policy
        self.namespace = namespace

        self._lock = RLock()
        self._topics: dict[str, set[_Sub]] = {}

    def subscribe(self, topic: str) -> Subscription:
        t = topic or "default"
        sub_lock = RLock()
        sub = _Sub(lock=sub_lock, cv=Condition(sub_lock), dq=deque())
        with self._lock:
            self._topics.setdefault(t, set()).add(sub)
        return Subscription(self, t, sub)

    def _unsubscribe(self, topic: str, sub: _Sub) -> None:
        with self._lock:
            s = self._topics.get(topic)
            if not s:
                return
            s.discard(sub)
            if not s:
                self._topics.pop(topic, None)
        with sub.lock:
            sub.closed = True
            sub.cv.notify_all()

    def publish(self, topic: str, msg: Any, *, timeout: float | None = None) -> int:
        t = topic or "default"
        deadline = None if timeout is None else (monotonic() + max(0.0, float(timeout)))
        with self._lock:
            subs = list(self._topics.get(t, ()))
        delivered = 0
        for sub in subs:
            with sub.lock:
                if sub.closed:
                    continue
                if len(sub.dq) >= self.max_backlog_per_sub:
                    if self.drop_policy == "drop_new":
                        continue
                    if self.drop_policy == "drop_old":
                        sub.dq.popleft()
                    else:  # block
                        while not sub.closed and len(sub.dq) >= self.max_backlog_per_sub:
                            if deadline is None:
                                sub.cv.wait()
                            else:
                                remain = deadline - monotonic()
                                if remain <= 0:
                                    break
                                sub.cv.wait(remain)
                        if sub.closed or len(sub.dq) >= self.max_backlog_per_sub:
                            continue
                sub.dq.append(msg)
                sub.cv.notify()
                delivered += 1
        return delivered

    def topics(self) -> list[str]:
        with self._lock:
            return sorted(self._topics.keys())
