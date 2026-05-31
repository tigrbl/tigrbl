from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload


@dataclass(slots=True)
class WebTransportLaneState:
    lane: str
    family: str
    exchange: str
    closed: bool = False
    chunks_received: int = 0
    chunks_sent: int = 0


@dataclass(slots=True)
class WebTransportSessionState:
    session_id: str
    accepted: bool = False
    closed: bool = False
    streams: dict[str, WebTransportLaneState] = field(default_factory=dict)
    datagrams_seen: set[str] = field(default_factory=set)

    def apply_event(
        self,
        *,
        event: str,
        channel: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, object]:
        if self.closed and event != "webtransport.close":
            raise ValueError("WebTransport session is closed")
        payload = dict(payload or {})
        self._validate_session_id(payload)
        projection = validate_webtransport_event_payload(
            event=event,
            channel=channel,
            payload=payload,
        )
        family = str(projection["family"])
        if family == "session":
            self._apply_session_event(event)
        elif family == "stream":
            self._apply_stream_event(event=event, channel=channel, payload=payload, projection=projection)
        elif family == "datagram":
            self._apply_datagram_event(payload)
        else:  # pragma: no cover - guarded by payload validator
            raise ValueError(f"unsupported WebTransport family {family!r}")
        return self.snapshot()

    def snapshot(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "accepted": self.accepted,
            "closed": self.closed,
            "streams": {
                stream_id: {
                    "lane": state.lane,
                    "family": state.family,
                    "exchange": state.exchange,
                    "closed": state.closed,
                    "chunks_received": state.chunks_received,
                    "chunks_sent": state.chunks_sent,
                }
                for stream_id, state in sorted(self.streams.items())
            },
            "datagrams_seen": tuple(sorted(self.datagrams_seen)),
        }

    def _validate_session_id(self, payload: dict[str, Any]) -> None:
        payload_session_id = payload.get("session_id")
        if payload_session_id is not None and str(payload_session_id) != self.session_id:
            raise ValueError("WebTransport payload session_id does not match session")

    def _apply_session_event(self, event: str) -> None:
        if event == "webtransport.accept":
            self.accepted = True
            return
        if event in {"webtransport.close", "webtransport.disconnect"}:
            self.closed = True
            for state in self.streams.values():
                state.closed = True

    def _apply_stream_event(
        self,
        *,
        event: str,
        channel: str,
        payload: dict[str, Any],
        projection: dict[str, object],
    ) -> None:
        stream_id = str(payload["stream_id"])
        state = self.streams.get(stream_id)
        lane = str(projection["lane"])
        if state is None:
            state = WebTransportLaneState(
                lane=lane,
                family=str(projection["family"]),
                exchange=str(projection["exchange"]),
            )
            self.streams[stream_id] = state
        elif state.lane != lane:
            raise ValueError("WebTransport stream_id lane metadata changed")
        if state.closed and event not in {
            "webtransport.stream.close",
            "webtransport.stream.reset",
            "webtransport.stream.stop_sending",
        }:
            raise ValueError("WebTransport stream is closed")
        if event in {
            "webtransport.stream.close",
            "webtransport.stream.reset",
            "webtransport.stream.stop_sending",
        }:
            state.closed = True
        elif channel == "receive":
            state.chunks_received += 1
        elif channel == "send":
            state.chunks_sent += 1

    def _apply_datagram_event(self, payload: dict[str, Any]) -> None:
        datagram_id = str(payload["datagram_id"])
        self.datagrams_seen.add(datagram_id)


__all__ = ["WebTransportLaneState", "WebTransportSessionState"]
