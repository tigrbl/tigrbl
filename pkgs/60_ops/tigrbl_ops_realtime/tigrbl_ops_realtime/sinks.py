from __future__ import annotations

from dataclasses import dataclass
import inspect
import json
from typing import Any, Awaitable, Callable, Mapping, Protocol, runtime_checkable
from uuid import uuid4


SendCallable = Callable[[dict[str, Any]], Awaitable[None] | None]


@dataclass(frozen=True, slots=True)
class RealtimeEnvelope:
    channel: str
    event: Any
    method: str = "realtime.publish"

    def jsonrpc(self) -> dict[str, Any]:
        return {
            "jsonrpc": "2.0",
            "method": self.method,
            "params": {"channel": self.channel, "event": self.event},
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

    async def send_realtime(self, envelope: RealtimeEnvelope) -> None:
        payload = json.dumps(
            envelope.jsonrpc(), separators=(",", ":"), default=str
        ).encode()
        emit_id = uuid4().hex
        await self.send_bytes(
            stream_id=f"{self.stream_id}-{emit_id}",
            payload=payload,
            framing="jsonrpc",
            more=False,
            emit_id=emit_id,
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

    async def close_stream(self, stream_id: str) -> None:
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
