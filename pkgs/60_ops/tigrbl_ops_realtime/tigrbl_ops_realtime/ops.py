from __future__ import annotations

import asyncio
from typing import Any, Dict, Mapping

from .broker import DEFAULT_BROKER, InMemoryRealtimeBroker
from .sinks import RealtimeSink, realtime_sink_from_context


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


def _broker(ctx: Any) -> InMemoryRealtimeBroker:
    state = _state(ctx)
    broker = state.get("broker") if isinstance(state, Mapping) else None
    return broker if isinstance(broker, InMemoryRealtimeBroker) else DEFAULT_BROKER


def _raw_sink(ctx: Any) -> Any:
    state = _state(ctx)
    if isinstance(state, Mapping) and state.get("sink") is not None:
        return state["sink"]
    return _ctx_get(ctx, "channel")


def _sink(ctx: Any) -> RealtimeSink | None:
    raw = _raw_sink(ctx)
    return realtime_sink_from_context(ctx, raw) if raw is not None else None


def _session_id(ctx: Any, sink: Any = None) -> str | None:
    state = _state(ctx)
    if isinstance(state, Mapping) and state.get("session_id") is not None:
        return str(state["session_id"])
    websocket = _ctx_get(ctx, "websocket")
    if isinstance(websocket, Mapping) and websocket.get("session_id") is not None:
        return str(websocket["session_id"])
    return f"sink:{id(sink)}" if sink is not None else None


async def publish(payload: Any, *, ctx: Any = None) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    event = body.get("event")
    jsonrpc = _ctx_get(ctx, "jsonrpc", {})
    method = str(body.get("method") or _ctx_get(jsonrpc, "method", "realtime.publish"))
    broker = _broker(ctx)
    result = await broker.publish(channel=channel, event=event, method=method)
    await asyncio.sleep(0)
    return {
        "published": True,
        "channel": channel,
        "event": event,
        "subscriber_count": result.subscriber_count,
        "delivered": result.queued,
        "queued": result.queued,
        "failed": result.failed,
        "dropped": result.dropped,
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


async def telemetry(payload: Any = None, *, ctx: Any = None) -> Dict[str, Any]:
    body = _body(payload or {})
    channel = body.get("channel")
    return _broker(ctx).metrics(str(channel) if channel is not None else None)


async def tail(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    stream = str(body.get("stream", body.get("channel", "default")))
    limit = int(body.get("limit", 50))
    return {"stream": stream, "limit": limit, "tailed": True}


async def upload(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    name = str(body.get("name", "blob"))
    content = body.get("content")
    size = len(content) if isinstance(content, (bytes, bytearray)) else body.get("size")
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
