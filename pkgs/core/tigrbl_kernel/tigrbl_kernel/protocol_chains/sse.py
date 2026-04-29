from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def compile_sse_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    heartbeat_seconds = binding.get("heartbeat_seconds")
    subevents = ["session.open", "stream.start", "message.emit"]
    if heartbeat_seconds is not None:
        subevents.append("heartbeat.emit")
    subevents.extend(("stream.end", "session.close"))
    return {
        "binding": "http.sse",
        "exchange": "server_stream",
        "family": "event_stream",
        "path": binding.get("path"),
        "subevents": tuple(subevents),
        "heartbeat": {
            "seconds": heartbeat_seconds,
            "subevent": "heartbeat.emit",
            "producer": "timer",
            "drains_message_producer": False,
        },
        "break_conditions": ("producer.exhausted", "disconnect"),
        "err_target": "transport.close",
        "completion_fence": "POST_EMIT",
        "error_ctx": {
            "binding": "http.sse",
            "family": "event_stream",
            "subevent": "message.emit",
        },
    }


__all__ = ["compile_sse_chain"]
