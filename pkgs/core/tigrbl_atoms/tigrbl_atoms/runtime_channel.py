from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from typing import Any


def create_channel_state(
    *,
    channel_id: str,
    binding: str,
    family: str,
    peer: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "channel_id": channel_id,
        "binding": binding,
        "family": family,
        "peer": dict(peer or {}),
        "open": True,
        "closed": False,
        "received_count": 0,
        "emit_count": 0,
        "completion_state": "idle",
    }


def transition_channel_state(
    state: Mapping[str, Any],
    *,
    subevent: str,
    payload_size: int | None = None,
    close_code: int | None = None,
    close_reason: str | None = None,
) -> dict[str, Any]:
    if state.get("closed"):
        raise ValueError("channel state transition rejected after closed")
    next_state = dict(state)
    next_state["current_subevent"] = subevent
    if payload_size is not None:
        next_state["last_payload_size"] = payload_size
    if subevent.endswith(".received"):
        next_state["received_count"] = int(next_state.get("received_count", 0)) + 1
    if subevent.endswith(".emit"):
        next_state["emit_count"] = int(next_state.get("emit_count", 0)) + 1
        next_state["completion_state"] = "pending"
    if subevent.endswith(".emit_complete"):
        next_state["completion_state"] = "complete"
    if subevent.endswith(".close"):
        next_state["open"] = False
        next_state["closed"] = True
        next_state["close_code"] = close_code
        if close_reason is not None:
            next_state["close_reason"] = close_reason
    return next_state


def build_channel_error_ctx(
    state: Mapping[str, Any],
    *,
    subevent: str,
    phase: str,
    exc: BaseException,
) -> dict[str, Any]:
    return {
        "channel_id": state.get("channel_id"),
        "binding": state.get("binding"),
        "family": state.get("family"),
        "subevent": subevent,
        "phase": phase,
        "message": str(exc),
    }


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
        projection: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        if self.closed and event != "webtransport.close":
            raise ValueError("WebTransport session is closed")
        payload = dict(payload or {})
        self._validate_session_id(payload)
        if projection is None:
            projection = self.project_event(
                event=event, channel=channel, payload=payload
            )
        family = str(projection["family"])
        if family == "session":
            self._apply_session_event(event)
        elif family == "stream":
            self._apply_stream_event(
                event=event,
                channel=channel,
                payload=payload,
                projection=projection,
            )
        elif family == "datagram":
            self._apply_datagram_event(payload)
        else:
            raise ValueError(f"unsupported WebTransport family {family!r}")
        return self.snapshot()

    def project_event(
        self,
        *,
        event: str,
        channel: str,
        payload: dict[str, Any],
    ) -> Mapping[str, object]:
        del channel, payload
        if event in {
            "webtransport.connect",
            "webtransport.accept",
            "webtransport.disconnect",
            "webtransport.close",
        }:
            return {
                "family": "session",
                "lane": "session",
                "exchange": "request_response",
            }
        raise ValueError(
            "WebTransport event projection is required for non-session events"
        )

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
        if (
            payload_session_id is not None
            and str(payload_session_id) != self.session_id
        ):
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
        projection: Mapping[str, object],
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


__all__ = [
    "build_channel_error_ctx",
    "create_channel_state",
    "transition_channel_state",
    "WebTransportLaneState",
    "WebTransportSessionState",
]
