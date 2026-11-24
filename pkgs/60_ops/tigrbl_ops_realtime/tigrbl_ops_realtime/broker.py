from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Callable, Mapping
from uuid import uuid4

from tigrbl_typing.trace import TraceSink, emit_trace

from .quotas import SubscriptionAdmission, SubscriptionLease, fence_delivery
from .sinks import RealtimeEnvelope, RealtimeSink, WebSocketRealtimeSink, WebTransportRealtimeSink


@dataclass(slots=True)
class RealtimeSubscription:
    session_id: str
    channel: str
    sink: RealtimeSink
    subscription_id: str = field(default_factory=lambda: f"sub_{uuid4().hex}")
    generation: str = field(default_factory=lambda: uuid4().hex)
    cursor: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    queue: asyncio.Queue[RealtimeEnvelope] = field(
        repr=False, default_factory=asyncio.Queue
    )
    worker: asyncio.Task[None] | None = field(repr=False, default=None)
    quota_lease: SubscriptionLease | None = field(repr=False, default=None)
    renewal: asyncio.Task[None] | None = field(repr=False, default=None)
    operation: str = "subscribe"
    delivered: int = 0
    failed: int = 0
    dropped: int = 0
    last_delivery_at: str | None = None


@dataclass(frozen=True, slots=True)
class PublicationResult:
    publication_id: str
    published_at: str
    subscriber_count: int
    queued: int
    dropped: int
    failed: int


class InMemoryRealtimeBroker:
    """Transport-neutral process-local fanout with bounded subscriber queues."""

    def __init__(
        self, *, queue_size: int = 128,
        authorize_subscription_resume: Callable[[Any, RealtimeSubscription, str], bool] | None = None,
        resume_ttl_seconds: float = 0,
        admission: SubscriptionAdmission | None = None,
        trace_sink: TraceSink | None = None,
    ) -> None:
        if queue_size < 1:
            raise ValueError("queue_size must be positive")
        self.queue_size = queue_size
        if not 0 <= resume_ttl_seconds < float("inf"):
            raise ValueError("resume_ttl_seconds must be finite and nonnegative")
        self.authorize_subscription_resume = authorize_subscription_resume
        self.resume_ttl_seconds = resume_ttl_seconds
        self.admission = admission
        self.trace_sink = trace_sink
        self._attachment_lock = asyncio.Lock()
        self._closed = False
        self._closed_sessions: dict[str, None] = {}
        self._subscriptions: dict[str, dict[str, RealtimeSubscription]] = {}
        self._by_id: dict[str, RealtimeSubscription] = {}
        self._by_session: dict[str, set[str]] = {}
        self._suspended: dict[str, tuple[RealtimeSubscription, asyncio.TimerHandle]] = {}
        self._delivery_events: deque[dict[str, Any]] = deque(maxlen=1024)

    @staticmethod
    def _carrier_name(subscription: RealtimeSubscription) -> str:
        if isinstance(subscription.sink, WebSocketRealtimeSink):
            return "WebSocket"
        if isinstance(subscription.sink, WebTransportRealtimeSink):
            return "WebTransport"
        return "Realtime"

    def _trace_attachment(self, kind: str, subscription: RealtimeSubscription) -> None:
        if self.trace_sink is None:
            return
        fields = {
            **subscription.metadata,
            "subscription_id": subscription.subscription_id,
            "transport_session_id": subscription.session_id,
            "attachment_generation": subscription.generation,
        }
        if subscription.quota_lease is not None:
            fields["lease_id"] = subscription.quota_lease.id
        emit_trace(self.trace_sink, kind, self._carrier_name(subscription), fields)

    def _attach(self, subscription: RealtimeSubscription, *, resumed: bool = False) -> None:
        self._subscriptions.setdefault(subscription.channel, {})[subscription.session_id] = subscription
        self._by_id[subscription.subscription_id] = subscription
        self._by_session.setdefault(subscription.session_id, set()).add(subscription.subscription_id)
        self._trace_attachment("Subscription resumed" if resumed else "Subscription opened", subscription)

    def _detach(self, subscription: RealtimeSubscription) -> bool:
        if self._by_id.get(subscription.subscription_id) is not subscription:
            return False
        del self._by_id[subscription.subscription_id]
        members = self._subscriptions[subscription.channel]
        del members[subscription.session_id]
        if not members:
            del self._subscriptions[subscription.channel]
        memberships = self._by_session[subscription.session_id]
        memberships.remove(subscription.subscription_id)
        if not memberships:
            del self._by_session[subscription.session_id]
        self._trace_attachment("Attachment detached", subscription)
        return True

    def delivery_events(self) -> tuple[dict[str, Any], ...]:
        return tuple(dict(event) for event in self._delivery_events)

    def _record_delivery(self, subscription: RealtimeSubscription, envelope: RealtimeEnvelope, outcome: str) -> None:
        row = {
            "delivery_id": envelope.notification_id,
            "publication_id": envelope.publication_id,
            "subscription_id": subscription.subscription_id,
            "transport_session_id": subscription.session_id,
            "attachment_generation": subscription.generation,
            **({"lease_id": subscription.quota_lease.id} if subscription.quota_lease else {}),
            **{
                key: subscription.metadata[key]
                for key in ("correlation_id", "stream_id", "stream_correlation_id")
                if key in subscription.metadata
            },
            "origin_invocation_id": envelope.origin_invocation_id,
            "origin_correlation_id": envelope.origin_correlation_id,
            "outcome": outcome,
        }
        self._delivery_events.append(row)
        if self.trace_sink is not None:
            emit_trace(self.trace_sink, "Delivery", self._carrier_name(subscription), {
                **subscription.metadata, **row,
            })

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

    def _start_delivery(self, subscription: RealtimeSubscription) -> None:
        if self._by_id.get(subscription.subscription_id) is not subscription:
            return
        subscription.worker = asyncio.create_task(self._deliver(subscription))
        if subscription.quota_lease is not None:
            subscription.renewal = asyncio.create_task(self._renew(subscription))

    async def subscribe(
        self,
        *,
        channel: str,
        sink: RealtimeSink,
        session_id: str,
        cursor: Any = None,
        metadata: Mapping[str, Any] | None = None,
        ctx: Any = None,
        operation: str = "subscribe",
    ) -> RealtimeSubscription:
        async with self._attachment_lock:
            if self._closed or session_id in self._closed_sessions:
                raise RuntimeError("subscription session is closed")
            lease = await self.admission.acquire(ctx, operation) if self.admission else None
            previous = self._subscriptions.get(channel, {}).get(session_id)
            if previous is not None:
                self._detach(previous)
            subscription = RealtimeSubscription(
                session_id=session_id, channel=channel, sink=sink, cursor=cursor,
                metadata=dict(metadata or {}), queue=asyncio.Queue(maxsize=self.queue_size),
                quota_lease=lease, operation=operation,
            )
            if lease is not None:
                subscription.generation = lease.generation
            self._attach(subscription)
        try:
            if previous is not None:
                await self._stop(previous)
        finally:
            self._start_delivery(subscription)
        return subscription

    async def resume(
        self,
        subscription_id: str,
        *,
        expected_generation: str,
        session_id: str,
        sink: RealtimeSink,
        authorize: Callable[[RealtimeSubscription, str], bool] | None = None,
        metadata: Mapping[str, Any] | None = None,
        ctx: Any = None,
    ) -> RealtimeSubscription:
        """Move one logical subscription after verifying its attachment and owner."""
        async with self._attachment_lock:
            suspended = self._suspended.get(subscription_id)
            previous = suspended[0] if suspended is not None else self._by_id.get(subscription_id)
            if previous is None or previous.generation != expected_generation:
                raise ValueError("stale subscription attachment")
            if self._closed or session_id in self._closed_sessions:
                raise ValueError("target subscription session is closed")
            if authorize is not None and authorize(previous, session_id) is not True:
                raise PermissionError("subscription resume denied")
            occupied = self._subscriptions.get(previous.channel, {}).get(session_id)
            if occupied is not None and occupied is not previous:
                raise ValueError("destination already has a channel subscription")
            lease = None
            if previous.quota_lease is not None and self.admission is not None:
                lease = await self.admission.resume(ctx, previous.quota_lease, previous.operation)
            elif authorize is None:
                raise PermissionError("subscription resume denied")
            attachment = dict(previous.metadata)
            for key in ("correlation_id", "connection_id", "transport_session_id",
                        "stream_id", "stream_correlation_id"):
                attachment.pop(key, None)
            attachment.update(metadata or {})
            replacement = replace(
                previous, session_id=session_id, sink=sink, metadata=attachment,
                generation=lease.generation if lease else uuid4().hex,
                quota_lease=lease, worker=None, renewal=None,
            )
            if suspended is not None:
                self._suspended.pop(subscription_id)
                suspended[1].cancel()
            else:
                self._detach(previous)
            self._attach(replacement, resumed=True)
        try:
            await self._stop(previous, retain_queue=True)
        finally:
            self._start_delivery(replacement)
        return replacement

    async def unsubscribe(self, *, channel: str, session_id: str) -> bool:
        async with self._attachment_lock:
            subscription = self._subscriptions.get(channel, {}).get(session_id)
            if subscription is None or not self._detach(subscription):
                return False
        await self._stop(subscription)
        return True

    async def unsubscribe_session(self, session_id: str) -> int:
        return await self._remove_session(session_id, retain_attachment=False)

    async def disconnect_session(self, session_id: str) -> int:
        return await self._remove_session(session_id, retain_attachment=bool(self.resume_ttl_seconds))

    async def _remove_session(self, session_id: str, *, retain_attachment: bool) -> int:
        async with self._attachment_lock:
            self._closed_sessions[session_id] = None
            if len(self._closed_sessions) > 4096:
                self._closed_sessions.pop(next(iter(self._closed_sessions)))
            subscriptions = [self._by_id[key] for key in self._by_session.get(session_id, ())]
            detached = [item for item in subscriptions if self._detach(item)]
        for subscription in detached:
            lease = subscription.quota_lease
            can_resume = retain_attachment and (
                lease is not None or (
                    callable(self.authorize_subscription_resume) and subscription.metadata.get("session_id")
                )
            )
            await self._stop(subscription, retain_lease=bool(can_resume))
            if can_resume:
                async with self._attachment_lock:
                    if not self._closed:
                        key = subscription.subscription_id
                        delay = self.resume_ttl_seconds
                        if lease is not None:
                            delay = min(delay, max(0, lease.deadline - lease.store.clock()))
                        expiry = asyncio.get_running_loop().call_later(
                            delay, self._schedule_expiration, key
                        )
                        self._suspended[key] = (subscription, expiry)
                        continue
                if lease is not None:
                    await lease.release()
        return len(detached)

    def _schedule_expiration(self, subscription_id: str) -> None:
        asyncio.create_task(self._expire_suspended(subscription_id))

    async def _expire_suspended(self, subscription_id: str) -> None:
        async with self._attachment_lock:
            suspended = self._suspended.pop(subscription_id, None)
            if suspended is None:
                return
            subscription, expiry = suspended
            expiry.cancel()
        await self._stop(subscription)

    async def revoke_identity(self, identity) -> int:
        async with self._attachment_lock:
            active = [
                item for item in self._by_id.values()
                if getattr(item.quota_lease, "identity", None) == identity
            ]
            for item in active:
                self._detach(item)
            suspended = [
                key for key, (item, _) in self._suspended.items()
                if getattr(item.quota_lease, "identity", None) == identity
            ]
        for item in active:
            await self._stop(item)
        for key in suspended:
            await self._expire_suspended(key)
        return len(active) + len(suspended)

    async def publish(
        self,
        *,
        channel: str,
        event: Any,
        method: str = "realtime.publish",
        publication_id: str | None = None,
        origin_invocation_id: str | None = None,
        origin_correlation_id: str | None = None,
    ) -> PublicationResult:
        subscriptions = tuple(self._subscriptions.get(channel, {}).values())
        resolved_publication_id = publication_id or f"pub_{uuid4().hex}"
        published_at = datetime.now(timezone.utc).isoformat()
        if self.trace_sink is not None:
            emit_trace(self.trace_sink, "Publication", "Realtime", {
                "publication_id": resolved_publication_id,
                "origin_invocation_id": origin_invocation_id,
                "origin_correlation_id": origin_correlation_id,
            })
        queued = dropped = 0
        for subscription in subscriptions:
            envelope = RealtimeEnvelope(
                channel=channel,
                event=event,
                method=method,
                publication_id=resolved_publication_id,
                notification_id=f"ntf_{uuid4().hex}",
                published_at=published_at,
                origin_invocation_id=origin_invocation_id,
                origin_correlation_id=origin_correlation_id,
            )
            try:
                subscription.queue.put_nowait(envelope)
                queued += 1
            except asyncio.QueueFull:
                subscription.dropped += 1
                dropped += 1
                self._record_delivery(subscription, envelope, "dropped")
        return PublicationResult(
            publication_id=resolved_publication_id,
            published_at=published_at,
            subscriber_count=len(subscriptions),
            queued=queued,
            dropped=dropped,
            failed=sum(item.failed for item in subscriptions),
        )

    async def close(self) -> None:
        async with self._attachment_lock:
            self._closed = True
            suspended = tuple(self._suspended)
            session_ids = tuple(self._by_session)
        for key in suspended:
            await self._expire_suspended(key)
        for session_id in session_ids:
            await self.unsubscribe_session(session_id)

    async def _deliver(self, subscription: RealtimeSubscription) -> None:
        try:
            while True:
                envelope = await subscription.queue.get()
                try:
                    lease = subscription.quota_lease
                    if lease is None:
                        await subscription.sink.send_realtime(envelope)
                    else:
                        await fence_delivery(lease)
                        remaining = lease.deadline - lease.store.clock()
                        await asyncio.wait_for(subscription.sink.send_realtime(envelope), max(0, remaining))
                except asyncio.CancelledError:
                    self._record_delivery(subscription, envelope, "cancelled")
                    raise
                except Exception:
                    subscription.failed += 1
                    self._record_delivery(subscription, envelope, "failed")
                    if self._detach(subscription):
                        await self._stop(subscription)
                    return
                else:
                    subscription.delivered += 1
                    self._record_delivery(subscription, envelope, "delivered")
                    subscription.last_delivery_at = datetime.now(
                        timezone.utc
                    ).isoformat()
                finally:
                    subscription.queue.task_done()
        except asyncio.CancelledError:
            raise

    async def _stop(
        self, subscription: RealtimeSubscription, *, retain_queue: bool = False, retain_lease: bool = False
    ) -> None:
        for task in (subscription.renewal, subscription.worker):
            if task is not None and task is not asyncio.current_task():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        if not retain_queue:
            while not subscription.queue.empty():
                envelope = subscription.queue.get_nowait()
                subscription.queue.task_done()
                self._record_delivery(subscription, envelope, "cancelled")
        if subscription.quota_lease is not None and not retain_lease:
            await subscription.quota_lease.release()

    async def _renew(self, subscription: RealtimeSubscription) -> None:
        lease = subscription.quota_lease
        assert lease is not None and self.admission is not None
        try:
            while True:
                await asyncio.sleep(self.admission.policy.lease_renewal_seconds)
                await lease.renew()
        except asyncio.CancelledError:
            raise
        except Exception:
            if self._detach(subscription):
                await self._stop(subscription)


DEFAULT_BROKER = InMemoryRealtimeBroker()

__all__ = [
    "DEFAULT_BROKER",
    "InMemoryRealtimeBroker",
    "PublicationResult",
    "RealtimeSubscription",
]
