from __future__ import annotations

from collections.abc import Mapping
from typing import Any


_BARRIERS = {
    "transport.accept": True,
    "transport.emit": True,
    "transport.close": True,
}


def compile_transport_atom_chain(*, binding: str, subevent: str) -> dict[str, object]:
    binding_name = str(binding)
    subevent_name = str(subevent)

    if binding_name in {"ws", "websocket"} and subevent_name == "message.received":
        anchors = ("transport.accept", "transport.receive", "framing.decode")
        return {
            "binding": "websocket",
            "subevent": subevent_name,
            "anchors": anchors,
            "barriers": dict(_BARRIERS),
            "err_target": "transport.close",
        }

    if binding_name in {"http.sse", "sse"} and subevent_name == "message.emit":
        anchors = ("framing.encode", "transport.emit", "transport.emit_complete")
        return {
            "binding": "http.sse",
            "subevent": subevent_name,
            "anchors": anchors,
            "barriers": dict(_BARRIERS),
            "err_target": "transport.close",
        }

    if binding_name in {"ws", "websocket"} and subevent_name == "session.close":
        anchors = ("transport.close",)
        return {
            "binding": "websocket",
            "subevent": subevent_name,
            "anchors": anchors,
            "barriers": dict(_BARRIERS),
            "err_target": "transport.close",
        }

    raise ValueError(f"unsupported transport atom chain: binding={binding_name} subevent={subevent_name}")


def as_segment(chain: Mapping[str, Any]) -> dict[str, object]:
    anchors = tuple(chain.get("anchors", ()))
    if not anchors:
        raise ValueError("transport atom chain requires anchors")
    head = anchors[0]
    segment_class = head if head in _BARRIERS else "pure_transport"
    return {
        "segment_id": f"{chain.get('binding', 'transport')}:{chain.get('subevent', 'unknown')}",
        "class": segment_class,
        "atoms": anchors,
        "err_target": chain.get("err_target"),
    }


__all__ = ["as_segment", "compile_transport_atom_chain"]
