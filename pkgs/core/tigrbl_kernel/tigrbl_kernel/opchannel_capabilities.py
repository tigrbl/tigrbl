from __future__ import annotations

from collections.abc import Iterable

CAPABILITY_BITS: dict[str, int] = {
    "accept": 1 << 0,
    "recv": 1 << 1,
    "send": 1 << 2,
    "close": 1 << 3,
    "events": 1 << 4,
    "chunks.send": 1 << 5,
    "datagrams.recv": 1 << 6,
    "datagrams.send": 1 << 7,
    "metrics": 1 << 8,
}

_REQUIREMENTS: dict[tuple[str, str], tuple[str, ...]] = {
    ("websocket", "message.received"): ("accept", "recv", "send", "close"),
    ("ws", "message.received"): ("accept", "recv", "send", "close"),
    ("sse", "message.emit"): ("send", "close"),
    ("http.sse", "message.emit"): ("send", "close"),
    ("stream", "chunk.emit"): ("chunks.send", "close"),
    ("http.stream", "chunk.emit"): ("chunks.send", "close"),
    ("webtransport", "datagram.received"): (
        "datagrams.recv",
        "datagrams.send",
        "close",
    ),
}


def capability_mask(capabilities: Iterable[str]) -> int:
    mask = 0
    for capability in capabilities:
        token = str(capability)
        bit = CAPABILITY_BITS.get(token)
        if bit is not None:
            mask |= bit
    return mask


def compile_capability_requirements(*, binding: str, subevent: str) -> dict[str, object]:
    required = _REQUIREMENTS.get((str(binding), str(subevent)), ("send", "close"))
    return {
        "binding": binding,
        "subevent": subevent,
        "required": required,
        "required_mask": capability_mask(required),
    }


__all__ = ["CAPABILITY_BITS", "capability_mask", "compile_capability_requirements"]
