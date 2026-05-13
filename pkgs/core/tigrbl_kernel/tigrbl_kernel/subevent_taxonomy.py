from __future__ import annotations


_FAMILIES = {
    "request": ("request.received", "request.body.received"),
    "response": ("response.emit", "response.emit_complete"),
    "session": ("session.open", "session.ready", "session.close"),
    "message": ("message.received", "message.decoded", "message.emit", "message.emit_complete"),
    "stream": ("stream.open", "stream.chunk.received", "stream.chunk.emit", "stream.close"),
    "datagram": ("datagram.received", "datagram.emit", "datagram.emit_complete"),
}

_BINDING_FAMILY = {
    "http.rest": "response",
    "http.jsonrpc": "response",
    "http.stream": "stream",
    "http.sse": "stream",
    "ws": "message",
    "websocket": "message",
    "webtransport.datagram": "datagram",
}

_ALIASES = {
    "receive": {"message": "message.received", "request": "request.received"},
    "emit": {"response": "response.emit", "message": "message.emit", "datagram": "datagram.emit"},
    "complete": {"response": "response.emit_complete", "message": "message.emit_complete", "datagram": "datagram.emit_complete"},
}


def derive_runtime_subevents(family: str) -> tuple[str, ...]:
    try:
        return _FAMILIES[family]
    except KeyError as exc:
        raise ValueError(f"unknown runtime subevent family: {family}") from exc


def derive_binding_subevents(binding: str) -> dict[str, object]:
    family = _BINDING_FAMILY[binding]
    return {"family": family, "subevents": derive_runtime_subevents(family)}


def resolve_channel_verb_alias(verb: str, *, family: str) -> str:
    return _ALIASES[verb][family]


def normalize_subevent(subevent: str, *, family: str | None = None) -> str:
    if "." in subevent:
        return subevent
    if family is None:
        raise ValueError("subevent aliases must be qualified with a family")
    return resolve_channel_verb_alias(subevent, family=family)


__all__ = [
    "derive_binding_subevents",
    "derive_runtime_subevents",
    "normalize_subevent",
    "resolve_channel_verb_alias",
]
