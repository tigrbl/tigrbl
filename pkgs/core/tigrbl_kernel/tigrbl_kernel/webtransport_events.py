from __future__ import annotations

from collections.abc import Sequence


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


__all__ = [
    "compile_webtransport_chain",
    "compile_webtransport_events",
    "compile_webtransport_native_lanes",
]
