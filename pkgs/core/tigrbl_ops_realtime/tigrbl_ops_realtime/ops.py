from __future__ import annotations

from typing import Any, Dict, Mapping


def _body(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise TypeError("Realtime operations require mapping payloads")
    return payload


async def publish(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    event = body.get("event")
    return {"published": True, "channel": channel, "event": event}


async def subscribe(payload: Any) -> Dict[str, Any]:
    body = _body(payload)
    channel = str(body.get("channel", "default"))
    cursor = body.get("cursor")
    return {"subscribed": True, "channel": channel, "cursor": cursor}


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
