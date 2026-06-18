from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Mapping
from enum import IntEnum
from typing import Any

from tigrbl_core._spec.binding_spec import validate_webtransport_inner_framing

UINT8_MAX_STREAMS = 256
UINT16_MAX_STREAMS = 65_536
_STREAM_EVENTS = {
    "webtransport.stream.receive",
    "webtransport.stream.send",
    "webtransport.stream.close",
    "webtransport.stream.reset",
    "webtransport.stream.stop_sending",
}
_DATAGRAM_EVENTS = {
    "webtransport.datagram.receive",
    "webtransport.datagram.send",
}
_SESSION_EVENTS = {
    "webtransport.connect",
    "webtransport.accept",
    "webtransport.disconnect",
    "webtransport.close",
}
_STREAM_DIRECTIONS = {
    "bidi": "bidi_stream",
    "client_to_server": "unidi_client_stream",
    "server_to_client": "unidi_server_stream",
}
_STREAM_DIRECTION_METADATA = {
    "bidi": "bidirectional",
    "client_to_server": "client_to_server",
    "server_to_client": "server_to_client",
}
_UNIDI_INITIATORS = {
    "client_to_server": "client",
    "server_to_client": "server",
}


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
    stream_initiator: str | None = None
    stream_direction: str | None = None
    direction: str | None = None
    lane_id: int | None = None
    stream_ordinal: int | None = None
    stream_id_width: str | None = None
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
                    "stream_initiator": state.stream_initiator,
                    "stream_direction": state.stream_direction,
                    "direction": state.direction,
                    "lane_id": state.lane_id,
                    "stream_ordinal": state.stream_ordinal,
                    "stream_id_width": state.stream_id_width,
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
        lane_metadata = self._stream_lane_metadata(payload=payload, projection=projection)
        if state is None:
            if len(self.streams) >= self.stream_id_provisioning.max_streams:
                raise ValueError("WebTransport session max_streams exceeded")
            state = WebTransportLaneState(
                lane=lane,
                family=str(projection["family"]),
                exchange=str(projection["exchange"]),
                stream_initiator=lane_metadata["stream_initiator"],
                stream_direction=lane_metadata["stream_direction"],
                direction=lane_metadata["direction"],
                lane_id=lane_metadata["lane_id"],
                stream_ordinal=lane_metadata["stream_ordinal"],
                stream_id_width=lane_metadata["stream_id_width"],
            )
            self.streams[stream_id] = state
        elif state.lane != lane:
            raise ValueError("WebTransport stream_id lane metadata changed")
        elif not self._same_stream_metadata(state, lane_metadata):
            raise ValueError("WebTransport stream_id initiator metadata changed")
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

    def _stream_lane_metadata(
        self,
        *,
        payload: dict[str, Any],
        projection: Mapping[str, object],
    ) -> dict[str, Any]:
        lane_id = projection.get("lane_id")
        if lane_id is None:
            lane_id = payload.get("lane_id")
        stream_ordinal = projection.get("stream_ordinal")
        stream_id_width = projection.get("stream_id_width")
        if lane_id is not None:
            lane = LaneId(int(lane_id), width=self.stream_id_provisioning.width)
            lane_id = lane.value
            stream_ordinal = lane.ordinal
            stream_id_width = lane.width.label
            inferred_initiator = "server" if lane.initiator is Initiator.SERVER else "client"
            inferred_direction = (
                "bidirectional" if lane.direction is Direction.BIDI else "unidi"
            )
            if projection.get("stream_initiator") is not None and str(
                projection["stream_initiator"]
            ) != inferred_initiator:
                raise ValueError("WebTransport lane_id initiator mismatch")
            if projection.get("direction") == "bidirectional" and inferred_direction != "bidirectional":
                raise ValueError("WebTransport lane_id direction mismatch")
            if projection.get("direction") in {"client_to_server", "server_to_client"} and inferred_direction != "unidi":
                raise ValueError("WebTransport lane_id direction mismatch")
        return {
            "stream_initiator": _optional_str(projection.get("stream_initiator")),
            "stream_direction": _optional_str(projection.get("stream_direction")),
            "direction": _optional_str(projection.get("direction")),
            "lane_id": lane_id,
            "stream_ordinal": stream_ordinal,
            "stream_id_width": _optional_str(stream_id_width),
        }

    def _same_stream_metadata(
        self,
        state: WebTransportLaneState,
        metadata: Mapping[str, Any],
    ) -> bool:
        for field in (
            "stream_initiator",
            "stream_direction",
            "direction",
            "lane_id",
            "stream_ordinal",
            "stream_id_width",
        ):
            current = getattr(state, field)
            proposed = metadata.get(field)
            if current is not None and proposed is not None and current != proposed:
                return False
        return True


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def validate_webtransport_event_payload(
    *,
    event: str,
    channel: str,
    payload: dict[str, Any],
) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("WebTransport event payload must be a mapping")
    if channel not in {"receive", "send"}:
        raise ValueError("WebTransport event channel must be receive or send")
    if event in _SESSION_EVENTS:
        return _validate_session_payload(event=event, channel=channel, payload=payload)
    if event in _STREAM_EVENTS:
        return _validate_stream_payload(event=event, channel=channel, payload=payload)
    if event in _DATAGRAM_EVENTS:
        return _validate_datagram_payload(event=event, channel=channel, payload=payload)
    if event.startswith("webtransport.message"):
        raise ValueError("WebTransport message is not a native transport lane")
    raise ValueError(f"unsupported WebTransport event {event!r}")


def _validate_session_payload(
    *,
    event: str,
    channel: str,
    payload: dict[str, Any],
) -> dict[str, object]:
    expected_channel = (
        "receive"
        if event in {"webtransport.connect", "webtransport.disconnect"}
        else "send"
    )
    if channel != expected_channel:
        raise ValueError(f"{event} is only valid on {expected_channel}")
    _forbid(
        payload,
        "stream_id",
        "stream_direction",
        "stream_initiator",
        "lane_id",
        "datagram_id",
        "framing",
    )
    return {"family": "session", "lane": "session", "exchange": "request_response"}


def _validate_stream_payload(
    *,
    event: str,
    channel: str,
    payload: dict[str, Any],
) -> dict[str, object]:
    expected_channel = "receive" if event == "webtransport.stream.receive" else "send"
    if channel != expected_channel:
        raise ValueError(f"{event} is only valid on {expected_channel}")
    _require(payload, "stream_id")
    _forbid(payload, "datagram_id")
    direction = payload.get("stream_direction")
    if event in {
        "webtransport.stream.receive",
        "webtransport.stream.send",
    }:
        if not isinstance(direction, str) or direction not in _STREAM_DIRECTIONS:
            raise ValueError("WebTransport stream payload requires valid stream_direction")
    else:
        direction = str(direction) if direction in _STREAM_DIRECTIONS else "bidi"
    lane = _STREAM_DIRECTIONS[str(direction)]
    stream_initiator = _stream_initiator(
        payload.get("stream_initiator"),
        stream_direction=str(direction),
    )
    if channel == "receive" and lane == "unidi_server_stream":
        raise ValueError("server_to_client unidirectional streams cannot be receive events")
    if channel == "send" and lane == "unidi_client_stream":
        raise ValueError("client_to_server unidirectional streams cannot be send events")
    validate_webtransport_inner_framing(
        lane=lane,
        inner_framing=payload.get("framing"),
    )
    projection = {
        "family": "stream",
        "lane": lane,
        "exchange": {
            "bidi_stream": "bidirectional_stream",
            "unidi_client_stream": "client_stream",
            "unidi_server_stream": "server_stream",
        }[lane],
        "stream_direction": str(direction),
        "direction": _STREAM_DIRECTION_METADATA[str(direction)],
        "stream_initiator": stream_initiator,
    }
    _copy_int_field(payload, projection, "lane_id")
    _copy_int_field(payload, projection, "stream_ordinal")
    if payload.get("stream_id_width") is not None:
        projection["stream_id_width"] = str(payload["stream_id_width"])
    return projection


def _validate_datagram_payload(
    *,
    event: str,
    channel: str,
    payload: dict[str, Any],
) -> dict[str, object]:
    expected_channel = "receive" if event == "webtransport.datagram.receive" else "send"
    if channel != expected_channel:
        raise ValueError(f"{event} is only valid on {expected_channel}")
    _require(payload, "datagram_id")
    _forbid(payload, "stream_id", "stream_direction", "stream_initiator", "lane_id")
    validate_webtransport_inner_framing(
        lane="datagram",
        inner_framing=payload.get("framing"),
    )
    return {"family": "datagram", "lane": "datagram", "exchange": "bidirectional_stream"}


def _require(payload: dict[str, Any], field: str) -> None:
    value = payload.get(field)
    if value is None or value == "":
        raise ValueError(f"WebTransport payload requires {field}")


def _forbid(payload: dict[str, Any], *fields: str) -> None:
    present = [field for field in fields if field in payload and payload[field] is not None]
    if present:
        joined = ", ".join(present)
        raise ValueError(f"WebTransport payload field not valid for event: {joined}")


def _stream_initiator(
    value: object,
    *,
    stream_direction: str,
) -> str:
    if stream_direction in _UNIDI_INITIATORS:
        expected = _UNIDI_INITIATORS[stream_direction]
        if value is not None and str(value) != expected:
            raise ValueError(f"{stream_direction} stream_initiator must be {expected}")
        return expected
    if value is None:
        return "client"
    token = str(value)
    if token not in {"client", "server"}:
        raise ValueError("WebTransport stream_initiator must be client or server")
    return token


def _copy_int_field(
    payload: dict[str, Any],
    projection: dict[str, object],
    field: str,
) -> None:
    value = payload.get(field)
    if value is None:
        return
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"WebTransport payload {field} must be an integer")
    projection[field] = value


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
    "validate_webtransport_event_payload",
]
