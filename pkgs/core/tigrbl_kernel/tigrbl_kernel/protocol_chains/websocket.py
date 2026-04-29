from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ANCHORS: tuple[str, ...] = (
    "transport.accept",
    "transport.receive",
    "framing.decode",
    "CALL_HANDLER",
    "framing.encode",
    "transport.emit",
    "transport.close",
)


def compile_websocket_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    scheme = binding.get("scheme", "ws")
    if scheme not in {"ws", "wss"}:
        raise ValueError("websocket scheme must be ws or wss")
    tls = dict((binding.get("extensions") or {}).get("tls") or {})
    return {
        "binding": "wss" if scheme == "wss" else "websocket",
        "exchange": "bidirectional_stream",
        "family": "message",
        "path": binding.get("path"),
        "anchors": ANCHORS,
        "loop_region": {
            "loop_id": "websocket.receive",
            "role": "message",
            "break_conditions": ("websocket.disconnect",),
        },
        "close": {"code": 1000, "reason": ""},
        "scope_metadata": {
            "secure": scheme == "wss",
            "tls": tls,
        },
    }


__all__ = ["compile_websocket_chain"]
