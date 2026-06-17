from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from tigrbl_core._spec.hook_spec import matches_hook_selector

from .webtransport_events import validate_webtransport_event_payload

WEBTRANSPORT_SUBEVENTS = {
    "webtransport.connect": "session.open",
    "webtransport.accept": "session.accept",
    "webtransport.disconnect": "session.close",
    "webtransport.close": "session.close",
    "webtransport.stream.receive": "stream.chunk.received",
    "webtransport.stream.send": "stream.chunk.emit",
    "webtransport.stream.close": "stream.close",
    "webtransport.stream.reset": "stream.close",
    "webtransport.stream.stop_sending": "stream.close",
    "webtransport.datagram.receive": "datagram.received",
    "webtransport.datagram.send": "datagram.emit",
}


def normalize_exchange(exchange: str | None) -> str:
    token = str(exchange or "request_response")
    if token == "bidirectional":
        return "bidirectional_stream"
    return token


def channel_family(scope_type: str, exchange: str) -> str:
    exchange = normalize_exchange(exchange)
    if scope_type == "websocket":
        return "socket"
    if scope_type == "webtransport":
        return "session"
    if exchange in {"server_stream", "client_stream", "bidirectional_stream"}:
        return "stream"
    if exchange == "fire_and_forget":
        return "request"
    return "response"


def channel_kind(scope_type: str, exchange: str) -> str:
    exchange = normalize_exchange(exchange)
    if scope_type == "websocket":
        return "websocket"
    if scope_type == "webtransport":
        return "webtransport"
    if exchange in {"server_stream", "client_stream", "bidirectional_stream"}:
        return "stream"
    if exchange == "event_stream":
        return "sse"
    return "http"


def channel_subevents(scope_type: str, exchange: str) -> tuple[str, ...]:
    exchange = normalize_exchange(exchange)
    if scope_type in {"websocket", "webtransport"}:
        return ("connect", "receive", "emit", "complete", "disconnect")
    if exchange in {"server_stream", "client_stream", "bidirectional_stream", "event_stream"}:
        return ("receive", "emit", "complete")
    return ("receive", "emit", "complete")


def webtransport_event_metadata(
    *,
    direction: str,
    message: Mapping[str, Any],
) -> dict[str, Any]:
    event_type = str(message.get("type") or "")
    metadata: dict[str, Any] = {
        "binding": "webtransport",
        "event_type": event_type,
        "type": event_type,
        "subevent": WEBTRANSPORT_SUBEVENTS.get(event_type, event_type),
        "framing": message.get("framing"),
    }
    try:
        projection = validate_webtransport_event_payload(
            event=event_type,
            channel=direction,
            payload=dict(message),
        )
    except ValueError:
        projection = {}
    for key in (
        "family",
        "lane",
        "exchange",
        "stream_initiator",
        "stream_direction",
        "direction",
        "lane_id",
        "stream_ordinal",
        "stream_id_width",
    ):
        if projection.get(key) is not None:
            metadata[key] = projection[key]
    if "family" not in metadata:
        if ".stream." in event_type:
            metadata["family"] = "stream"
        elif ".datagram." in event_type:
            metadata["family"] = "datagram"
        else:
            metadata["family"] = "session"
    if "lane" not in metadata:
        metadata["lane"] = metadata["family"]
    if "exchange" not in metadata:
        metadata["exchange"] = "request_response"
    return metadata


def select_webtransport_hooks(
    hooks: Iterable[Any],
    *,
    direction: str,
    metadata: Mapping[str, Any],
) -> tuple[Any, ...]:
    allowed_phases = (
        {"PRE_HANDLER", "HANDLER"}
        if direction == "receive"
        else {"POST_HANDLER", "POST_RESPONSE"}
    )
    return tuple(
        hook
        for hook in hooks
        if str(getattr(hook.phase, "value", hook.phase)) in allowed_phases
        if matches_hook_selector(hook, metadata)
    )


__all__ = [
    "WEBTRANSPORT_SUBEVENTS",
    "channel_family",
    "channel_kind",
    "channel_subevents",
    "normalize_exchange",
    "select_webtransport_hooks",
    "webtransport_event_metadata",
]
