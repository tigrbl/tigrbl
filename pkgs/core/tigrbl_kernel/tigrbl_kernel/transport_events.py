from __future__ import annotations

from collections.abc import Iterable, Mapping


_KNOWN_TRANSPORTS = {
    "http": {
        "scope_type": "http",
        "events": (
            ("http.request", "inbound", True, "request.received"),
            ("http.response.start", "outbound", True, "response.start"),
            ("http.response.body", "outbound", True, "response.emit"),
        ),
    },
    "websocket": {
        "scope_type": "websocket",
        "events": (
            ("websocket.connect", "inbound", True, "session.open"),
            ("websocket.receive", "inbound", True, "message.received"),
            ("websocket.send", "outbound", True, "message.emit"),
            ("websocket.close", "outbound", True, "session.close"),
        ),
    },
    "webtransport": {
        "scope_type": "webtransport",
        "events": (
            ("webtransport.connect", "inbound", True, "session.open"),
            ("webtransport.datagram.receive", "inbound", True, "datagram.received"),
            ("webtransport.stream.receive", "inbound", True, "stream.chunk.received"),
            ("webtransport.close", "outbound", True, "session.close"),
        ),
    },
    "lifespan": {
        "scope_type": "lifespan",
        "events": (
            ("lifespan.startup", "inbound", True, "session.open"),
            ("lifespan.shutdown", "inbound", True, "session.close"),
        ),
    },
    "static_file": {
        "scope_type": "http",
        "events": (
            ("static_file.lookup", "inbound", True, "request.received"),
            ("static_file.emit", "outbound", True, "response.emit"),
        ),
    },
    "callback": {
        "scope_type": None,
        "events": (("callback.emit", "outbound", False, "message.emit"),),
    },
    "webhook": {
        "scope_type": "http",
        "events": (("webhook.emit", "outbound", False, "message.emit"),),
    },
}


def build_transport_event_registry() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for transport, config in _KNOWN_TRANSPORTS.items():
        scope_type = config["scope_type"]
        for event_name, direction, required, subevent in config["events"]:
            rows.append(
                {
                    "event": event_name,
                    "transport": transport,
                    "direction": direction,
                    "required": required,
                    "scope_type": scope_type,
                    "subevent": subevent,
                    "extension_namespace": "asgi" if "." in event_name else None,
                }
            )
    return rows


def validate_transport_event_registry(rows: Iterable[Mapping[str, object]]) -> list[dict[str, object]]:
    normalized = [dict(row) for row in rows]
    seen: set[str] = set()
    known_events = {entry["event"] for entry in build_transport_event_registry()}

    for row in normalized:
        event_name = str(row.get("event"))
        transport = str(row.get("transport"))
        direction = str(row.get("direction"))
        scope_type = row.get("scope_type")

        if event_name in seen:
            raise ValueError("duplicate transport event registry event")
        seen.add(event_name)

        if event_name not in known_events:
            raise ValueError("unknown transport event registry event")

        if direction not in {"inbound", "outbound"}:
            raise ValueError("invalid direction in transport registry scope mapping")

        expected_scope = _KNOWN_TRANSPORTS.get(transport, {}).get("scope_type")
        if expected_scope != scope_type:
            raise ValueError("invalid direction or scope mapping for transport registry")

    return normalized


__all__ = ["build_transport_event_registry", "validate_transport_event_registry"]
