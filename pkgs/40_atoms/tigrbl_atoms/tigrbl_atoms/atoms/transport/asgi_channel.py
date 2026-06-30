from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def message_payload(message: Mapping[str, Any]) -> Any:
    payload = message.get("bytes")
    if payload is None:
        payload = message.get("data")
    if payload is None and message.get("text") is not None:
        payload = str(message.get("text")).encode("utf-8")
    return payload


def payload_size(message: Mapping[str, Any]) -> int | None:
    payload = message_payload(message)
    if isinstance(payload, (bytes, bytearray)):
        return len(payload)
    if isinstance(payload, str):
        return len(payload.encode("utf-8"))
    return None


def session_payload_events(
    payload: Any,
    *,
    accept_type: str,
    send_type: str,
    close_type: str,
) -> tuple[dict[str, Any], ...]:
    events: list[dict[str, Any]] = [{"type": accept_type}]
    if payload is not None:
        if isinstance(payload, (bytes, bytearray)):
            events.append({"type": send_type, "bytes": bytes(payload)})
        elif isinstance(payload, str):
            events.append({"type": send_type, "text": payload})
        else:
            events.append(
                {
                    "type": send_type,
                    "text": json.dumps(payload, separators=(",", ":"), default=str),
                }
            )
    events.append({"type": close_type, "code": 1000})
    return tuple(events)


def webtransport_payload_event(
    *,
    base: Mapping[str, Any],
    payload: Any,
) -> dict[str, Any]:
    event_type = str(base.get("type") or "")
    session_id = base.get("session_id")
    if event_type == "webtransport.stream.receive":
        out: dict[str, Any] = {
            "type": "webtransport.stream.send",
            "session_id": session_id,
            "stream_id": base.get("stream_id"),
            "stream_direction": base.get("stream_direction", "bidi"),
        }
        if base.get("stream_initiator") is not None:
            out["stream_initiator"] = base.get("stream_initiator")
        elif out["stream_direction"] == "bidi":
            out["stream_initiator"] = "client"
        if base.get("framing") is not None:
            out["framing"] = base.get("framing")
        if isinstance(payload, (bytes, bytearray)):
            out["data"] = bytes(payload)
        elif isinstance(payload, str):
            out["data"] = payload.encode("utf-8")
        else:
            out["data"] = json.dumps(
                payload, separators=(",", ":"), default=str
            ).encode("utf-8")
        out["more"] = False
        return out
    if event_type == "webtransport.datagram.receive":
        out = {
            "type": "webtransport.datagram.send",
            "session_id": session_id,
            "datagram_id": base.get("datagram_id"),
        }
        if base.get("framing") is not None:
            out["framing"] = base.get("framing")
        if isinstance(payload, (bytes, bytearray)):
            out["data"] = bytes(payload)
        elif isinstance(payload, str):
            out["data"] = payload.encode("utf-8")
        else:
            out["data"] = json.dumps(
                payload, separators=(",", ":"), default=str
            ).encode("utf-8")
        return out
    out = {"type": "webtransport.send", "session_id": session_id}
    if isinstance(payload, (bytes, bytearray)):
        out["bytes"] = bytes(payload)
    elif isinstance(payload, str):
        out["text"] = payload
    else:
        out["text"] = json.dumps(payload, separators=(",", ":"), default=str)
    return out


def _coerce_webtransport_stream_id(value: Any, *, fallback: int) -> Any:
    if value is None or value == "":
        return fallback
    return value


def _row_for_lane(rows: Any, *, lane_id: Any, index: int) -> Mapping[str, Any]:
    if not isinstance(rows, list) or not rows:
        return {}
    for row in rows:
        if isinstance(row, Mapping) and str(row.get("id") or "") == str(lane_id):
            return row
    if index < len(rows) and isinstance(rows[index], Mapping):
        return rows[index]
    return {}


def webtransport_structured_payload_events(
    *,
    session_id: Any,
    inbound: Mapping[str, Any] | list[Mapping[str, Any]],
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    inbound_events = inbound if isinstance(inbound, list) else [inbound]
    bidi_index = 0
    for current in inbound_events:
        inbound_type = str(current.get("type") or "")
        inbound_stream_id = _coerce_webtransport_stream_id(
            current.get("stream_id"),
            fallback=4 + bidi_index,
        )
        inbound_direction = str(current.get("stream_direction") or "bidi")
        framing = current.get("framing")

        if (
            inbound_type == "webtransport.stream.receive"
            and inbound_direction == "bidi"
        ):
            row = _row_for_lane(
                payload.get("bidirectional_streams"),
                lane_id=inbound_stream_id,
                index=bidi_index,
            )
            bidi_index += 1
            message = row.get("message") if isinstance(row, Mapping) else None
            if message is None:
                message = payload.get("message")
            if message is None:
                message = "demo-bidirectional"
            event: dict[str, Any] = {
                "type": "webtransport.stream.send",
                "session_id": session_id,
                "stream_id": inbound_stream_id,
                "stream_direction": "bidi",
                "stream_initiator": current.get("stream_initiator", "client"),
                "data": str(message).encode("utf-8"),
                "more": False,
            }
            if framing is not None:
                event["framing"] = framing
            events.append(event)

    first_inbound_stream_id = next(
        (
            item.get("stream_id")
            for item in inbound_events
            if str(item.get("type") or "") == "webtransport.stream.receive"
        ),
        None,
    )
    numeric_stream_base: int | None = None
    try:
        numeric_stream_base = int(first_inbound_stream_id)
    except Exception:
        numeric_stream_base = None

    uni_rows = payload.get("unidirectional_streams")
    if isinstance(uni_rows, list):
        for index, row in enumerate(uni_rows):
            if not isinstance(row, Mapping):
                continue
            message = row.get("message")
            if message is None:
                continue
            stream_id: Any = row.get("id") or f"server-stream-{index + 1}"
            if numeric_stream_base is not None:
                try:
                    stream_id = int(stream_id)
                except Exception:
                    stream_id = numeric_stream_base + index + 1
            event = {
                "type": "webtransport.stream.send",
                "session_id": session_id,
                "stream_id": stream_id,
                "stream_direction": "server_to_client",
                "stream_initiator": "server",
                "data": str(message).encode("utf-8"),
                "more": False,
            }
            row_framing = row.get("framing") if isinstance(row, Mapping) else None
            if row_framing is not None:
                event["framing"] = row_framing
            events.append(event)

    datagram_rows = payload.get("datagrams")
    inbound_datagram_ids = [
        item.get("datagram_id")
        for item in inbound_events
        if str(item.get("type") or "") == "webtransport.datagram.receive"
        and item.get("datagram_id") is not None
    ]
    inbound_datagram_framings = [
        item.get("framing")
        for item in inbound_events
        if str(item.get("type") or "") == "webtransport.datagram.receive"
        and item.get("framing") is not None
    ]
    if isinstance(datagram_rows, list):
        for index, row in enumerate(datagram_rows):
            if not isinstance(row, Mapping):
                continue
            if str(row.get("direction") or "") == "client-to-server":
                continue
            body = row.get("payload")
            if body is None:
                continue
            event = {
                "type": "webtransport.datagram.send",
                "session_id": session_id,
                "datagram_id": str(
                    row.get("id")
                    or (
                        inbound_datagram_ids[index]
                        if index < len(inbound_datagram_ids)
                        else None
                    )
                    or f"datagram-{index + 1}"
                ),
                "data": str(body).encode("utf-8"),
            }
            row_framing = row.get("framing") if isinstance(row, Mapping) else None
            if row_framing is None and index < len(inbound_datagram_framings):
                row_framing = inbound_datagram_framings[index]
            if row_framing is not None:
                event["framing"] = row_framing
            events.append(event)
    return events


def complete_channel_state(state: dict[str, Any]) -> dict[str, Any]:
    state["completed"] = True
    state["completion_fence"] = "POST_EMIT"
    return state


__all__ = [
    "complete_channel_state",
    "message_payload",
    "payload_size",
    "session_payload_events",
    "webtransport_payload_event",
    "webtransport_structured_payload_events",
]
