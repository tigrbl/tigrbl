from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Dict, Mapping


def _body(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("Realtime operations require mapping payloads")
    return payload


def _ctx_get(ctx: Any, key: str, default: Any = None) -> Any:
    if isinstance(ctx, Mapping):
        return ctx.get(key, default)
    return getattr(ctx, key, default)


def _state(ctx: Any) -> Mapping[str, Any]:
    realtime = _ctx_get(ctx, "realtime")
    if isinstance(realtime, Mapping):
        return realtime
    temp = _ctx_get(ctx, "temp")
    if isinstance(temp, Mapping):
        realtime = temp.get("realtime")
        if isinstance(realtime, Mapping):
            return realtime
    return {}


def _broker(ctx: Any) -> "InMemoryRealtimeBroker":
    state = _state(ctx)
    broker = state.get("broker") if isinstance(state, Mapping) else None
    if isinstance(broker, InMemoryRealtimeBroker):
        return broker
    return DEFAULT_BROKER


def _sink(ctx: Any) -> Any:
    state = _state(ctx)
    if isinstance(state, Mapping):
        sink = state.get("sink")
        if sink is not None:
            return sink
    return _ctx_get(ctx, "channel")


def _session_id(ctx: Any, sink: Any = None) -> str | None:
    state = _state(ctx)
    if isinstance(state, Mapping):
        value = state.get("session_id")
        if value is not None:
            return str(value)
    websocket = _ctx_get(ctx, "websocket")
    if isinstance(websocket, Mapping):
        value = websocket.get("session_id")
        if value is not None:
            return str(value)
    if sink is not None:
        return f"sink:{id(sink)}"
    return None


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


@dataclass
class RealtimeSubscription:
    session_id: str
    channel: str
    sink: Any
    cursor: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


class InMemoryRealtimeBroker:
    """Session-scoped broker for local WebSocket realtime delivery."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, dict[str, RealtimeSubscription]] = {}

    def subscriber_count(self, channel: str) -> int:
        return len(self._subscriptions.get(str(channel), {}))

    async def subscribe(
        self,
        *,
        channel: str,
        sink: Any,
        session_id: str,
        cursor: Any = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> RealtimeSubscription:
        subscription = RealtimeSubscription(
            session_id=session_id,
            channel=channel,
            sink=sink,
            cursor=cursor,
            metadata=dict(metadata or {}),
        )
        self._subscriptions.setdefault(channel, {})[session_id] = subscription
        return subscription

    async def unsubscribe_session(self, session_id: str) -> int:
        removed = 0
        for channel in list(self._subscriptions):
            channel_subs = self._subscriptions[channel]
            if session_id in channel_subs:
                del channel_subs[session_id]
                removed += 1
            if not channel_subs:
                del self._subscriptions[channel]
        return removed

    async def publish(
        self,
        *,
        channel: str,
        event: Any,
        method: str = "realtime.publish",
    ) -> int:
        delivered = 0
        for subscription in tuple(self._subscriptions.get(channel, {}).values()):
            if subscription.sink is None:
                continue
            await self._emit(
                subscription.sink,
                channel=channel,
                event=event,
                method=method,
            )
            delivered += 1
        return delivered

    async def _emit(self, sink: Any, *, channel: str, event: Any, method: str) -> None:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": {"channel": channel, "event": event},
        }
        message = {
            "type": "websocket.send",
            "text": json.dumps(payload, separators=(",", ":"), default=str),
        }
        send = getattr(sink, "send", None)
        if callable(send):
            await _maybe_await(send(message))
            return
        emit = getattr(sink, "emit", None)
        if callable(emit):
            await _maybe_await(emit(message))
            return
        if callable(sink):
            await _maybe_await(sink(message))


DEFAULT_BROKER = InMemoryRealtimeBroker()


async def publish(payload: Any, *, ctx: Any = None) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    event = body.get("event")
    jsonrpc = _ctx_get(ctx, "jsonrpc", {})
    method = str(body.get("method") or _ctx_get(jsonrpc, "method", "realtime.publish"))
    broker = _broker(ctx)
    delivered = await broker.publish(channel=channel, event=event, method=method)
    return {
        "published": True,
        "channel": channel,
        "event": event,
        "delivered": delivered,
        "subscriber_count": broker.subscriber_count(channel),
    }


async def subscribe(payload: Any, *, ctx: Any = None) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    cursor = body.get("cursor")
    sink = _sink(ctx)
    session_id = _session_id(ctx, sink)
    broker = _broker(ctx)
    if sink is not None and session_id is not None:
        await broker.subscribe(
            channel=channel,
            sink=sink,
            session_id=session_id,
            cursor=cursor,
            metadata={"payload": dict(body)},
        )
    return {
        "subscribed": True,
        "channel": channel,
        "cursor": cursor,
        "subscription_id": session_id,
        "subscriber_count": broker.subscriber_count(channel),
    }


async def unsubscribe_session(
    ctx: Any = None,
    *,
    session_id: str | None = None,
) -> Dict[str, Any]:
    resolved = session_id or _session_id(ctx)
    removed = await _broker(ctx).unsubscribe_session(resolved) if resolved else 0
    return {"unsubscribed": bool(removed), "removed": removed, "session_id": resolved}


async def tail(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    stream = str(body.get("stream", body.get("channel", "default")))
    limit = int(body.get("limit", 50))
    return {"stream": stream, "limit": limit, "tailed": True}


async def upload(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    name = str(body.get("name", "blob"))
    size = len(body.get("content", b"")) if isinstance(body.get("content"), (bytes, bytearray)) else body.get("size")
    return {"uploaded": True, "name": name, "size": size}


async def download(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    name = str(body.get("name", "blob"))
    return {"downloaded": True, "name": name, "checkpoint": body.get("checkpoint")}


async def append_chunk(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    stream = str(body.get("stream", "default"))
    chunk = body.get("chunk", b"")
    size = len(chunk) if isinstance(chunk, (bytes, bytearray, str)) else None
    return {"appended": True, "stream": stream, "size": size}


async def send_datagram(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    route = str(body.get("route", body.get("channel", "default")))
    return {"sent": True, "route": route, "ttl": body.get("ttl")}


async def checkpoint(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    cursor = body.get("cursor") or body.get("offset") or body.get("sequence")
    return {"checkpointed": True, "cursor": cursor}
