from __future__ import annotations

from typing import Any

from .pubsub import PubSubHub, Subscription


class PubSubSession:
    def __init__(self, engine: PubSubHub) -> None:
        self._engine = engine
        self._closed = False

    def close(self) -> None:
        self._closed = True

    def publish(self, topic: str, msg: Any, *, timeout: float | None = None) -> int:
        self._require_open()
        return self._engine.publish(topic, msg, timeout=timeout)

    def subscribe(self, topic: str) -> Subscription:
        self._require_open()
        return self._engine.subscribe(topic)

    def topics(self) -> list[str]:
        self._require_open()
        return self._engine.topics()

    def _require_open(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")


class AsyncPubSubSession(PubSubSession):
    async def close(self) -> None:  # type: ignore[override]
        super().close()
