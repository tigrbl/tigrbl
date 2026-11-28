from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SERVER_STREAM_ANCHORS: tuple[str, ...] = (
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

CLIENT_STREAM_ANCHORS: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "request.body.receive",
    "stream.chunk.received",
    "stream.receive_complete",
    "operation.resolve",
    "handler.call",
    "transport.emit_complete",
)


def compile_http_stream_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    exchange = str(binding.get("exchange") or "server_stream")
    if exchange == "client_stream":
        consumer = binding.get("consumer", "request_body")
        if consumer not in {"request_body", "async_iterator"}:
            raise ValueError("consumer must be request_body or async_iterator for HTTP client stream")
        return {
            "binding": "http.stream",
            "exchange": "client_stream",
            "family": "stream",
            "path": binding.get("path"),
            "method": binding.get("method", "POST"),
            "consumer": consumer,
            "anchors": CLIENT_STREAM_ANCHORS,
            "break_conditions": ("request.body_complete", "disconnect"),
            "err_target": "transport.close",
            "completion_fence": "POST_HANDLER",
        }
    if exchange != "server_stream":
        raise ValueError("HTTP stream exchange must be server_stream or client_stream")
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
        "anchors": SERVER_STREAM_ANCHORS,
        "break_conditions": ("producer.exhausted", "disconnect"),
        "err_target": "transport.close",
        "completion_fence": "POST_EMIT",
    }


__all__ = ["compile_http_stream_chain"]
