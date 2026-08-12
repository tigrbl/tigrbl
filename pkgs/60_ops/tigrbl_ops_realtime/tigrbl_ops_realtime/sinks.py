from __future__ import annotations

import asyncio
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime, timezone
import inspect
import json
import struct
from typing import Any, Awaitable, Callable, Mapping, Protocol, runtime_checkable
from uuid import uuid4


SendCallable = Callable[[dict[str, Any]], Awaitable[None] | None]


@dataclass(frozen=True, slots=True)
class RealtimeEnvelope:
    channel: str
    event: Any
    method: str = "realtime.publish"
    publication_id: str = field(default_factory=lambda: f"pub_{uuid4().hex}")
    notification_id: str = field(default_factory=lambda: f"ntf_{uuid4().hex}")
    published_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def jsonrpc(self) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": {
                "publication_id": self.publication_id,
                "notification_id": self.notification_id,
                "published_at": self.published_at,
                "channel": self.channel,
                "event": self.event,
            },
        }


@runtime_checkable
class RealtimeSink(Protocol):
    async def send_realtime(self, envelope: RealtimeEnvelope) -> None: ...


async def _send(call: SendCallable, message: dict[str, Any]) -> None:
    result = call(message)
    if inspect.isawaitable(result):
        await result


def _resolve_send(carrier: Any) -> SendCallable:
    send = getattr(carrier, "send", None)
    if callable(send):
        return send
    emit = getattr(carrier, "emit", None)
    if callable(emit):
        return emit
    if callable(carrier):
        return carrier
    raise TypeError("Realtime sink carrier must be callable or expose send/emit")


@dataclass(slots=True)
class WebSocketRealtimeSink:
    carrier: Any

    async def send_realtime(self, envelope: RealtimeEnvelope) -> None:
        payload = json.dumps(envelope.jsonrpc(), separators=(",", ":"), default=str)
        await _send(
            _resolve_send(self.carrier), {"type": "websocket.send", "text": payload}
        )


@dataclass(slots=True)
class WebTransportRealtimeSink:
    carrier: Any
    session_id: str
    stream_id: str = "realtime-events"
    _send_lock: asyncio.Lock = field(
        default_factory=asyncio.Lock, init=False, repr=False
    )
    _closed_streams: set[str] = field(default_factory=set, init=False, repr=False)

    async def send_realtime(self, envelope: RealtimeEnvelope) -> None:
        payload = json.dumps(
            envelope.jsonrpc(), separators=(",", ":"), default=str
        ).encode()
        await self.send_bytes(
            stream_id=self.stream_id,
            payload=struct.pack("!I", len(payload)) + payload,
            framing="jsonrpc",
            more=True,
        )

    async def send_bytes(
        self,
        *,
        stream_id: str,
        payload: bytes,
        framing: str = "bytes",
        more: bool = True,
        emit_id: str | None = None,
    ) -> None:
        async with self._send_lock:
            if stream_id in self._closed_streams:
                raise RuntimeError(f"WebTransport stream {stream_id!r} is closed")
            await _send(
                _resolve_send(self.carrier),
                {
                    "type": "webtransport.stream.send",
                    "session_id": self.session_id,
                    "stream_id": stream_id,
                    "stream_direction": "server_to_client",
                    "framing": framing,
                    "data": bytes(payload),
                    "more": more,
                    "emit_id": emit_id or uuid4().hex,
                },
            )
            if not more:
                self._closed_streams.add(stream_id)

    async def close_stream(self, stream_id: str) -> None:
        async with self._send_lock:
            if stream_id in self._closed_streams:
                return
            await _send(
                _resolve_send(self.carrier),
                {
                    "type": "webtransport.stream.close",
                    "session_id": self.session_id,
                    "stream_id": stream_id,
                    "stream_direction": "server_to_client",
                    "emit_id": uuid4().hex,
                },
            )
            self._closed_streams.add(stream_id)


def realtime_sink_from_context(ctx: Any, carrier: Any) -> RealtimeSink:
    if isinstance(carrier, RealtimeSink):
        return carrier
    state: Mapping[str, Any] = {}
    if isinstance(ctx, Mapping):
        candidate = ctx.get("realtime")
        if isinstance(candidate, Mapping):
            state = candidate
    else:
        candidate = getattr(ctx, "realtime", None)
        if isinstance(candidate, Mapping):
            state = candidate
    transport = str(state.get("transport") or getattr(ctx, "transport", "websocket"))
    if transport == "webtransport":
        session_id = state.get("session_id") or getattr(ctx, "session_id", None)
        if not session_id:
            raise ValueError("WebTransport realtime sinks require a session_id")
        return WebTransportRealtimeSink(
            carrier=carrier,
            session_id=str(session_id),
            stream_id=str(state.get("event_stream_id", "realtime-events")),
        )
    return WebSocketRealtimeSink(carrier=carrier)


__all__ = [
    "RealtimeEnvelope",
    "RealtimeSink",
    "WebSocketRealtimeSink",
    "WebTransportRealtimeSink",
    "realtime_sink_from_context",
]
