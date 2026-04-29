from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ANCHORS: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "operation.resolve",
    "handler.call",
    "iterator.producer.start",
    "transport.emit",
    "transport.emit_complete",
)


def compile_http_stream_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    producer = binding.get("producer", "iterator")
    if producer not in {"iterator", "async_iterator"}:
        raise ValueError("producer must be iterator or async_iterator for HTTP stream")
    return {
        "binding": "http.stream",
        "exchange": "server_stream",
        "family": "stream",
        "path": binding.get("path"),
        "method": binding.get("method", "GET"),
        "producer": producer,
        "anchors": ANCHORS,
        "break_conditions": ("producer.exhausted", "disconnect"),
        "err_target": "transport.close",
        "completion_fence": "POST_EMIT",
    }


__all__ = ["compile_http_stream_chain"]
