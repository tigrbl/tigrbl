from __future__ import annotations

import asyncio
import json
import struct
from collections import deque
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from tigrbl_atoms.atoms.framing import WebTransportRecordDecoder
from tigrbl_atoms.atoms.transport.asgi_channel import (
    disconnect_presentation_hub,
    disconnect_realtime_broker,
    disconnect_realtime_stream,
    webtransport_scope_session_id,
    webtransport_scope_state,
)
from tigrbl_atoms.runtime_channel import WebTransportSessionState

from .session_lifecycle import SessionTermination

STREAM_TERMINATION_EVENTS = frozenset(
    {
        "webtransport.stream.close",
        "webtransport.stream.reset",
        "webtransport.stream.stop_sending",
    }
)
MAX_EAGER_DRAIN_EVENTS = 16


@dataclass(slots=True)
class WebTransportSessionPlan:
    """Session-scoped carrier plan for framed control records.

    The plan owns record decoder state across ASGI receive calls. One inbound
    carrier chunk may yield zero, one, or several operation-dispatch events;
    completing any one operation does not complete the bidirectional stream.
    """

    pending: deque[dict[str, Any]] = field(default_factory=deque)
    control_decoders: dict[str, WebTransportRecordDecoder] = field(default_factory=dict)

    closed_streams: set[str] = field(default_factory=set)
    termination: SessionTermination = field(default_factory=SessionTermination)

    async def run(
        self,
        scope: dict[str, Any],
        invoke: Callable[[], Awaitable[None]],
        snapshot: Callable[[dict[str, Any]], None],
    ) -> None:
        state = webtransport_scope_state(scope)
        state["session_plan"] = self
        app = scope["app"]

        def close_lanes() -> None:
            self.close()
            session = state.get("session")
            if isinstance(session, WebTransportSessionState):
                session.close()
            state.get("stream_correlations", {}).clear()

        try:
            while not state.get("closed") and not state.get("disconnected"):
                await invoke()
                snapshot(state)
        finally:
            state["closed"] = True
            session = state.get("session")
            session_id = (
                session.session_id
                if isinstance(session, WebTransportSessionState)
                else webtransport_scope_session_id(scope)
            )
            await self.termination.run(
                close_lanes,
                lambda: disconnect_realtime_broker(
                    getattr(app, "__realtime_broker__", None), session_id
                ),
                lambda: disconnect_presentation_hub(
                    getattr(app, "__presentation_hub__", None), session_id
                ),
            )

    async def terminate_stream(self, scope: dict[str, Any], stream_id: str) -> None:
        if stream_id in self.closed_streams:
            return
        self.closed_streams.add(stream_id)
        state = webtransport_scope_state(scope)
        session = state.get("session")
        if not isinstance(session, WebTransportSessionState):
            return

        broker = getattr(scope.get("app"), "__realtime_broker__", None)
        await SessionTermination().run(
            lambda: session.close_stream(stream_id),
            lambda: state.get("stream_correlations", {}).pop(stream_id, None),
            lambda: disconnect_realtime_stream(broker, session.session_id, stream_id),
        )

    async def _read(
        self, receive: Callable[[], Awaitable[Mapping[str, Any]]]
    ) -> dict[str, Any]:
        while not self.pending:
            self.project_receive(await receive())
        return self.pending.popleft()

    async def _read_during_drain(
        self, receive: Callable[[], Awaitable[Mapping[str, Any]]]
    ) -> dict[str, Any] | None:
        if self.pending:
            return self.pending.popleft()
        reading = asyncio.create_task(self._read(receive))
        try:
            done, _ = await asyncio.wait((reading,), timeout=0.001)
            return reading.result() if done else None
        finally:
            if not reading.done():
                reading.cancel()
            await asyncio.gather(reading, return_exceptions=True)

    async def receive_unit(
        self,
        receive: Callable[[], Awaitable[Mapping[str, Any]]],
        record: Callable[[Mapping[str, Any]], Awaitable[None]],
        *,
        eager_drain: bool,
    ) -> None:
        event = await self._read(receive)
        while (
            event.get("type") in STREAM_TERMINATION_EVENTS
            or event.get("type") == "webtransport.connect"
        ):
            await record(event)
            event = await self._read(receive)
        await record(event)
        if not eager_drain or event.get("jsonrpc_complete"):
            return
        for _ in range(MAX_EAGER_DRAIN_EVENTS):
            if event.get("type") == "webtransport.disconnect":
                break
            next_event = await self._read_during_drain(receive)
            if next_event is None:
                break
            event = next_event
            if (
                event.get("jsonrpc_complete")
                or event.get("type") in STREAM_TERMINATION_EVENTS
            ):
                self.pending.appendleft(event)
                break
            await record(event)

    def has_pending(self) -> bool:
        return bool(self.pending)

    def pop_pending(self) -> dict[str, Any]:
        return self.pending.popleft()

    def project_receive(self, message: Mapping[str, Any]) -> None:
        event = dict(message)
        event_type = event.get("type")
        stream_id = str(event.get("stream_id"))
        if event_type in STREAM_TERMINATION_EVENTS:
            if stream_id in self.closed_streams:
                return
            self.control_decoders.pop(stream_id, None)
        elif (
            event_type == "webtransport.stream.receive"
            and stream_id in self.closed_streams
        ):
            return
        if (
            event_type != "webtransport.stream.receive"
            or str(event.get("stream_direction") or "bidi") != "bidi"
            or event.get("framing") not in {None, "jsonrpc"}
        ):
            self.pending.append(event)
            return
        data = event.get("data")
        if data is None:
            data = event.get("bytes")
        if not isinstance(data, (bytes, bytearray, memoryview)):
            self.pending.append(event)
            return
        raw = bytes(data)
        decoder = self.control_decoders.get(stream_id)
        if decoder is None and raw.lstrip().startswith((b"{", b"[")):
            # Compatibility for unframed peers while declared framed bindings
            # migrate. New peers must use uint32 big-endian record boundaries.
            self.pending.append(event)
            return
        if decoder is None and len(raw) >= 4:
            declared_size = struct.unpack_from("!I", raw, 0)[0]
            if declared_size > 3 * 1024 * 1024:
                self.pending.append(event)
                return
        if decoder is None:
            decoder = WebTransportRecordDecoder()
            self.control_decoders[stream_id] = decoder
        more = event.get("more")
        records = decoder.feed(raw, final=more is False)
        if more is False:
            self.control_decoders.pop(stream_id, None)
        for index, record in enumerate(records):
            projected = dict(event)
            projected.pop("bytes", None)
            projected["data"] = json.dumps(record, separators=(",", ":")).encode(
                "utf-8"
            )
            projected["framing"] = "jsonrpc"
            projected["jsonrpc_complete"] = True
            projected["more"] = more is not False or index < len(records) - 1
            self.pending.append(projected)

    def close(self) -> None:
        self.pending.clear()
        self.control_decoders.clear()
        self.closed_streams.clear()


__all__ = ["WebTransportSessionPlan"]
