from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from .sinks import RealtimeEnvelope, RealtimeSink


@dataclass(slots=True)
class RealtimeSubscription:
    session_id: str
    channel: str
    sink: RealtimeSink
    cursor: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    queue: asyncio.Queue[RealtimeEnvelope] = field(
        repr=False, default_factory=asyncio.Queue
    )
    worker: asyncio.Task[None] | None = field(repr=False, default=None)
    delivered: int = 0
    failed: int = 0
    dropped: int = 0
    last_delivery_at: str | None = None


@dataclass(frozen=True, slots=True)
class PublicationResult:
    subscriber_count: int
    queued: int
    dropped: int
    failed: int


class InMemoryRealtimeBroker:
    """Transport-neutral process-local fanout with bounded subscriber queues."""

    def __init__(self, *, queue_size: int = 128) -> None:
        if queue_size < 1:
            raise ValueError("queue_size must be positive")
        self.queue_size = queue_size
        self._subscriptions: dict[str, dict[str, RealtimeSubscription]] = {}

    def subscriber_count(self, channel: str) -> int:
        return len(self._subscriptions.get(str(channel), {}))

    def metrics(self, channel: str | None = None) -> dict[str, Any]:
        subscriptions = [
            subscription
            for name, members in self._subscriptions.items()
            if channel is None or name == str(channel)
            for subscription in members.values()
        ]
        return {
            "subscriber_count": len(subscriptions),
            "queue_depth": sum(item.queue.qsize() for item in subscriptions),
            "delivered": sum(item.delivered for item in subscriptions),
            "failed": sum(item.failed for item in subscriptions),
            "dropped": sum(item.dropped for item in subscriptions),
            "last_delivery_at": max(
                (
                    item.last_delivery_at
                    for item in subscriptions
                    if item.last_delivery_at
                ),
                default=None,
            ),
        }

    async def subscribe(
        self,
        *,
        channel: str,
        sink: RealtimeSink,
        session_id: str,
        cursor: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RealtimeSubscription:
        await self.unsubscribe(channel=channel, session_id=session_id)
        subscription = RealtimeSubscription(
            session_id=session_id,
            channel=channel,
            sink=sink,
            cursor=cursor,
            metadata=dict(metadata or {}),
            queue=asyncio.Queue(maxsize=self.queue_size),
        )
        self._subscriptions.setdefault(channel, {})[session_id] = subscription
        subscription.worker = asyncio.create_task(self._deliver(subscription))
        return subscription

    async def unsubscribe(self, *, channel: str, session_id: str) -> bool:
        members = self._subscriptions.get(channel)
        subscription = members.pop(session_id, None) if members else None
        if members == {}:
            self._subscriptions.pop(channel, None)
        if subscription is None:
            return False
        await self._stop(subscription)
        return True

    async def unsubscribe_session(self, session_id: str) -> int:
        channels = [
            name
            for name, members in self._subscriptions.items()
            if session_id in members
        ]
        removed = 0
        for channel in channels:
            removed += int(
                await self.unsubscribe(channel=channel, session_id=session_id)
            )
        return removed

    async def publish(
        self,
        *,
        channel: str,
        event: Any,
        method: str = "realtime.publish",
    ) -> PublicationResult:
        subscriptions = tuple(self._subscriptions.get(channel, {}).values())
        envelope = RealtimeEnvelope(channel=channel, event=event, method=method)
        queued = dropped = 0
        for subscription in subscriptions:
            try:
                subscription.queue.put_nowait(envelope)
                queued += 1
            except asyncio.QueueFull:
                subscription.dropped += 1
                dropped += 1
        return PublicationResult(
            subscriber_count=len(subscriptions),
            queued=queued,
            dropped=dropped,
            failed=sum(item.failed for item in subscriptions),
        )

    async def close(self) -> None:
        session_ids = {
            subscription.session_id
            for members in self._subscriptions.values()
            for subscription in members.values()
        }
        for session_id in session_ids:
            await self.unsubscribe_session(session_id)

    async def _deliver(self, subscription: RealtimeSubscription) -> None:
        try:
            while True:
                envelope = await subscription.queue.get()
                try:
                    await subscription.sink.send_realtime(envelope)
                except Exception:
                    subscription.failed += 1
                    await self.unsubscribe(
                        channel=subscription.channel,
                        session_id=subscription.session_id,
                    )
                    return
                else:
                    subscription.delivered += 1
                    subscription.last_delivery_at = datetime.now(
                        timezone.utc
                    ).isoformat()
                finally:
                    subscription.queue.task_done()
        except asyncio.CancelledError:
            raise

    async def _stop(self, subscription: RealtimeSubscription) -> None:
        worker = subscription.worker
        if worker is None or worker is asyncio.current_task():
            return
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass


DEFAULT_BROKER = InMemoryRealtimeBroker()

__all__ = [
    "DEFAULT_BROKER",
    "InMemoryRealtimeBroker",
    "PublicationResult",
    "RealtimeSubscription",
]
