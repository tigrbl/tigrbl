from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from enum import IntEnum
from typing import Any

from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload

UINT8_MAX_STREAMS = 256
UINT16_MAX_STREAMS = 65_536


class Initiator(IntEnum):
    CLIENT = 0
    SERVER = 1


class Direction(IntEnum):
    BIDI = 0
    UNI = 1


class StreamIdWidth(IntEnum):
    UINT8 = 8
    UINT16 = 16

    @property
    def label(self) -> str:
        return f"uint{int(self)}"


@dataclass(frozen=True, slots=True)
class LaneId:
    value: int
    width: StreamIdWidth = StreamIdWidth.UINT8

    def __post_init__(self) -> None:
        if isinstance(self.value, bool) or not isinstance(self.value, int):
            raise ValueError("lane_id must be an integer")
        width = StreamIdWidth(self.width)
        object.__setattr__(self, "width", width)
        max_value = (1 << int(width)) - 1
        if not 0 <= self.value <= max_value:
            raise ValueError(f"lane_id must fit {width.label}")

    @property
    def initiator(self) -> Initiator:
        return Initiator(self.value & 0b01)

    @property
    def direction(self) -> Direction:
        return Direction((self.value >> 1) & 0b01)

    @property
    def ordinal(self) -> int:
        return self.value >> 2

    @staticmethod
    def encode(
        *,
        initiator: Initiator,
        direction: Direction,
        ordinal: int,
        width: StreamIdWidth = StreamIdWidth.UINT8,
    ) -> "LaneId":
        initiator = Initiator(initiator)
        direction = Direction(direction)
        width = StreamIdWidth(width)
        if isinstance(ordinal, bool) or not isinstance(ordinal, int):
            raise ValueError("ordinal must be an integer")
        ordinal_bits = int(width) - 2
        max_ordinal = (1 << ordinal_bits) - 1
        if not 0 <= ordinal <= max_ordinal:
            raise ValueError(f"ordinal must fit in {ordinal_bits} bits")
        value = (ordinal << 2) | (int(direction) << 1) | int(initiator)
        return LaneId(value, width=width)


@dataclass(frozen=True, slots=True)
class WebTransportStreamIdProvisioning:
    max_streams: int

    def __post_init__(self) -> None:
        if isinstance(self.max_streams, bool) or not isinstance(self.max_streams, int):
            raise ValueError("max WT streams must be an integer")
        if not 1 <= self.max_streams <= UINT16_MAX_STREAMS:
            raise ValueError("max WT streams must be between 1 and uint16")

    @property
    def width(self) -> StreamIdWidth:
        if self.max_streams <= UINT8_MAX_STREAMS:
            return StreamIdWidth.UINT8
        return StreamIdWidth.UINT16

    @property
    def lanes_per_transport_class(self) -> int:
        return 1 << (int(self.width) - 2)

    @property
    def total_lanes(self) -> int:
        return 1 << int(self.width)

    def encode_lane(
        self,
        *,
        initiator: Initiator,
        direction: Direction,
        ordinal: int,
    ) -> LaneId:
        return LaneId.encode(
            initiator=initiator,
            direction=direction,
            ordinal=ordinal,
            width=self.width,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "max_streams": self.max_streams,
            "width": self.width.label,
            "lanes_per_transport_class": self.lanes_per_transport_class,
            "total_lanes": self.total_lanes,
        }


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
    max_streams: int = UINT8_MAX_STREAMS
    streams: dict[str, WebTransportLaneState] = field(default_factory=dict)
    datagrams_seen: set[str] = field(default_factory=set)
    stream_id_provisioning: WebTransportStreamIdProvisioning = field(init=False)

    def __post_init__(self) -> None:
        self.stream_id_provisioning = WebTransportStreamIdProvisioning(
            max_streams=self.max_streams
        )

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
        return validate_webtransport_event_payload(
            event=event,
            channel=channel,
            payload=payload,
        )

    def snapshot(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "accepted": self.accepted,
            "closed": self.closed,
            "stream_id_provisioning": self.stream_id_provisioning.as_dict(),
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

    def provision_lane_id(
        self,
        *,
        initiator: Initiator,
        direction: Direction,
        ordinal: int,
    ) -> LaneId:
        return self.stream_id_provisioning.encode_lane(
            initiator=initiator,
            direction=direction,
            ordinal=ordinal,
        )

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
            if len(self.streams) >= self.stream_id_provisioning.max_streams:
                raise ValueError("WebTransport session max_streams exceeded")
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
    "Direction",
    "Initiator",
    "LaneId",
    "StreamIdWidth",
    "UINT8_MAX_STREAMS",
    "UINT16_MAX_STREAMS",
    "WebTransportStreamIdProvisioning",
    "build_channel_error_ctx",
    "create_channel_state",
    "transition_channel_state",
    "WebTransportLaneState",
    "WebTransportSessionState",
]
