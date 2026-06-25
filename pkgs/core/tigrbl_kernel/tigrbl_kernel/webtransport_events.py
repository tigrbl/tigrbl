from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from tigrbl_core._spec.binding_spec import (
    framing_spec_from_kind,
    validate_webtransport_inner_framing,
)


def _event(subevent: str, atom: str, family: str) -> dict[str, str]:
    return {"subevent": subevent, "atom": atom, "family": family}


def compile_webtransport_events(surface: str) -> list[dict[str, str]]:
    if surface == "session":
        return [
            _event("session.open", "transport.accept", "session"),
            _event("session.accept", "transport.accept", "session"),
            _event("session.ready", "transport.emit", "session"),
            _event("session.close", "transport.close", "session"),
        ]
    if surface == "stream":
        return [
            _event("stream.open", "transport.accept", "stream"),
            _event("stream.chunk.received", "transport.receive", "stream"),
            _event("stream.chunk.emit", "transport.emit", "stream"),
            _event("stream.emit_complete", "transport.emit", "stream"),
            _event("stream.close", "transport.close", "stream"),
        ]
    if surface == "bidi_stream":
        return [
            _event("stream.open", "transport.accept", "stream"),
            _event("stream.chunk.received", "transport.receive", "stream"),
            _event("stream.chunk.emit", "transport.emit", "stream"),
            _event("stream.close", "transport.close", "stream"),
        ]
    if surface == "unidi_client_stream":
        return [
            _event("stream.open", "transport.accept", "stream"),
            _event("stream.chunk.received", "transport.receive", "stream"),
            _event("stream.close", "transport.close", "stream"),
        ]
    if surface == "unidi_server_stream":
        return [
            _event("stream.open", "transport.accept", "stream"),
            _event("stream.chunk.emit", "transport.emit", "stream"),
            _event("stream.emit_complete", "transport.emit", "stream"),
            _event("stream.close", "transport.close", "stream"),
        ]
    if surface == "datagram":
        return [
            _event("datagram.received", "transport.receive", "datagram"),
            _event("datagram.emit", "transport.emit", "datagram"),
            _event("datagram.emit_complete", "transport.emit", "datagram"),
        ]
    if surface == "app_frame":
        return [
            _event("app_frame.decode", "framing.decode", "stream"),
            _event("app_frame.emit", "transport.emit", "stream"),
            _event("app_frame.encode", "framing.encode", "stream"),
        ]
    if surface == "message":
        raise ValueError("WebTransport does not expose message as a native surface")
    raise ValueError(f"unsupported WebTransport surface: {surface}")


def compile_webtransport_chain(*, include_stream: bool = True, include_datagram: bool = True) -> dict[str, Sequence[str]]:
    subevents: list[str] = [event["subevent"] for event in compile_webtransport_events("session")[:-1]]
    if include_stream:
        subevents.extend(event["subevent"] for event in compile_webtransport_events("stream"))
    if include_datagram:
        subevents.extend(event["subevent"] for event in compile_webtransport_events("datagram"))
    subevents.append("session.close")
    return {"binding": "webtransport", "subevents": tuple(subevents)}


def compile_webtransport_native_lanes() -> dict[str, tuple[str, ...]]:
    return {
        "session": tuple(event["subevent"] for event in compile_webtransport_events("session")),
        "bidi_stream": tuple(event["subevent"] for event in compile_webtransport_events("bidi_stream")),
        "unidi_client_stream": tuple(
            event["subevent"] for event in compile_webtransport_events("unidi_client_stream")
        ),
        "unidi_server_stream": tuple(
            event["subevent"] for event in compile_webtransport_events("unidi_server_stream")
        ),
        "datagram": tuple(event["subevent"] for event in compile_webtransport_events("datagram")),
    }


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
    expected_channel = "receive" if event in {"webtransport.connect", "webtransport.disconnect"} else "send"
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
        channel=channel,
    )
    if channel == "receive" and lane == "unidi_server_stream":
        raise ValueError("server_to_client unidirectional streams cannot be receive events")
    if channel == "send" and lane == "unidi_client_stream":
        raise ValueError("client_to_server unidirectional streams cannot be send events")
    validate_webtransport_inner_framing(
        lane=lane,
        inner_framing=framing_spec_from_kind(payload.get("framing")),
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
        inner_framing=framing_spec_from_kind(payload.get("framing")),
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
    channel: str,
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
    "compile_webtransport_chain",
    "compile_webtransport_events",
    "compile_webtransport_native_lanes",
    "validate_webtransport_event_payload",
]
