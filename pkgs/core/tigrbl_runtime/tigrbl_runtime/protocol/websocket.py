from __future__ import annotations

import inspect
from collections.abc import Mapping
from typing import Any


async def run_websocket_chain(config: Mapping[str, Any]) -> dict[str, object]:
    scope = config.get("scope") or {}
    messages = tuple(config.get("messages") or ())
    handler = config.get("handler")
    received: list[object] = []
    received_text: list[str] = []
    received_bytes: list[bytes] = []
    close_code = 1000
    close_reason = ""

    for message in messages:
        if not isinstance(message, Mapping):
            continue
        msg_type = message.get("type")
        if msg_type == "websocket.receive":
            item = message.get("text") if "text" in message else message.get("bytes")
            if isinstance(item, str):
                received_text.append(item)
            if isinstance(item, bytes):
                received_bytes.append(item)
            received.append(item)
            try:
                if callable(handler):
                    value = handler(item)
                    if inspect.isawaitable(value):
                        await value
            except Exception as exc:
                return {
                    "accepted": True,
                    "received": received,
                    "closed": True,
                    "close_code": 1011,
                    "error_ctx": {
                        "binding": "wss" if scope.get("scheme") == "wss" else "websocket",
                        "subevent": "message.received",
                        "message": str(exc),
                    },
                }
        elif msg_type == "websocket.disconnect":
            close_code = int(message.get("code", close_code))
            close_reason = str(message.get("reason", close_reason))
            break

    return {
        "accepted": True,
        "received": received,
        "received_text": received_text,
        "received_bytes": received_bytes,
        "closed": True,
        "close_code": close_code,
        "close_reason": close_reason,
    }


__all__ = ["run_websocket_chain"]
