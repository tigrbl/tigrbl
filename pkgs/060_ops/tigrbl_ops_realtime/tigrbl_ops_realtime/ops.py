from __future__ import annotations

import asyncio
from typing import Any, Dict, Mapping

from .broker import DEFAULT_BROKER, InMemoryRealtimeBroker
from .sinks import RealtimeSink, WebTransportRealtimeSink, realtime_sink_from_context


def _body(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("Realtime operations require mapping payloads")
    return payload


def _publication_id(body: Mapping[str, Any]) -> str | None:
    value = body.get("publication_id")
    if value is None:
        return None
    resolved = str(value).strip()
    if not resolved:
        raise ValueError("publication_id must not be empty")
    if len(resolved) > 200:
        raise ValueError("publication_id must be at most 200 characters")
    return resolved


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


def _identity(ctx: Any) -> Mapping[str, Any]:
    identity = _ctx_get(ctx, "identity")
    if isinstance(identity, Mapping):
        return identity
    temp = _ctx_get(ctx, "temp")
    if isinstance(temp, Mapping) and isinstance(temp.get("identity"), Mapping):
        return temp["identity"]
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
    return realtime_sink_from_context(ctx, raw, realtime=_state(ctx)) if raw is not None else None


def _session_id(ctx: Any, sink: Any = None) -> str | None:
    transport_session = _identity(ctx).get("transport_session_id")
    if transport_session is not None:
        return str(transport_session)
    state = _state(ctx)
    if isinstance(state, Mapping) and state.get("session_id") is not None:
        return str(state["session_id"])
    websocket = _ctx_get(ctx, "websocket")
    if isinstance(websocket, Mapping) and websocket.get("session_id") is not None:
        return str(websocket["session_id"])
    return f"sink:{id(sink)}" if sink is not None else None


def _attachment_identity(ctx: Any, sink: RealtimeSink) -> Dict[str, Any]:
    identity = dict(_identity(ctx))
    if isinstance(sink, WebTransportRealtimeSink):
        project_stream = _state(ctx).get("identity_for_stream")
        identity.pop("stream_correlation_id", None)
        identity["stream_id"] = sink.stream_id
        if callable(project_stream):
            identity.update(project_stream(sink.stream_id))
    return identity


async def publish(payload: Any, *, ctx: Any = None) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    event = body.get("event")
    jsonrpc = _ctx_get(ctx, "jsonrpc", {})
    method = str(body.get("method") or _ctx_get(jsonrpc, "method", "realtime.publish"))
    broker = _broker(ctx)
    result = await broker.publish(
        channel=channel,
        event=event,
        method=method,
        publication_id=_publication_id(body),
        origin_invocation_id=_identity(ctx).get("invocation_id"),
        origin_correlation_id=_identity(ctx).get("correlation_id"),
    )
    await asyncio.sleep(0)
    return {
        "published": True,
        "publication_id": result.publication_id,
        "published_at": result.published_at,
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
    subscription = None
    if sink is not None and session_id is not None:
        subscription = await broker.subscribe(
            channel=channel,
            sink=sink,
            session_id=session_id,
            cursor=cursor,
            ctx=ctx,
            operation=str(_ctx_get(_ctx_get(ctx, "jsonrpc", {}), "method", "subscribe")),
            metadata={
                "payload": dict(body), **_attachment_identity(ctx, sink),
                "opening_invocation_id": _identity(ctx).get("invocation_id"),
                "opening_correlation_id": _identity(ctx).get("correlation_id"),
            },
        )
    response = {
        "subscribed": subscription is not None,
        "channel": channel,
        "cursor": cursor,
        "subscription_id": session_id if subscription is not None else None,
        "subscriber_count": broker.subscriber_count(channel),
    }
    if _state(ctx).get("subscription_ack_version") == 2:
        response["subscription_id"] = subscription.subscription_id if subscription is not None else None
        response["transport_session_id"] = session_id
        if subscription is not None and (broker.admission is not None or callable(_resume_policy(ctx))):
            response["attachment_generation"] = subscription.generation
    return response


def _resume_policy(ctx: Any) -> Any:
    return _state(ctx).get("authorize_subscription_resume") or _broker(ctx).authorize_subscription_resume


async def resume_subscription(payload: Any, *, ctx: Any = None) -> Dict[str, Any]:
    """Resume a subscription through an application-supplied authorization policy."""
    body = _body(payload)
    sink = _sink(ctx)
    destination = _session_id(ctx, sink)
    authorize = _resume_policy(ctx)
    broker = _broker(ctx)
    if (broker.admission is None and not callable(authorize)) or sink is None or destination is None:
        raise PermissionError("subscription resume denied")

    subscription_id = body.get("subscription_id")
    generation = body.get("attachment_generation")
    if not isinstance(subscription_id, str) or not isinstance(generation, str):
        raise ValueError("resume requires subscription_id and attachment_generation")
    subscription = await broker.resume(
        subscription_id,
        expected_generation=generation,
        session_id=destination,
        sink=sink,
        authorize=(lambda previous, target: authorize(ctx, previous, target)) if callable(authorize) else None,
        ctx=ctx,
        metadata=_attachment_identity(ctx, sink),
    )
    return {
        "subscribed": True,
        "channel": subscription.channel,
        "subscription_id": subscription.subscription_id,
        "transport_session_id": subscription.session_id,
        "attachment_generation": subscription.generation,
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
