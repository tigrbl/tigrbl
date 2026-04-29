from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REST_ANCHORS: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "operation.resolve",
    "handler.call",
    "response.shape",
    "transport.emit",
    "transport.emit_complete",
)

JSONRPC_ANCHORS: tuple[str, ...] = (
    "transport.ingress",
    "binding.match",
    "framing.decode",
    "dispatch.exchange.select",
    "dispatch.family.derive",
    "dispatch.subevent.derive",
    "operation.resolve",
    "handler.call",
    "response.shape",
    "framing.encode",
    "transport.emit",
    "transport.emit_complete",
)


def compile_http_rest_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    if binding.get("binding", "http.rest") != "http.rest":
        raise ValueError("binding unsupported; expected http.rest or http.jsonrpc")
    return {
        "binding": "http.rest",
        "exchange": "request_response",
        "family": "response",
        "method": binding.get("method"),
        "path": binding.get("path"),
        "anchors": REST_ANCHORS,
        "completion_fence": "POST_EMIT",
    }


def compile_http_jsonrpc_chain(binding: Mapping[str, Any]) -> dict[str, object]:
    if binding.get("binding", "http.jsonrpc") != "http.jsonrpc":
        raise ValueError("binding unsupported; expected http.rest or http.jsonrpc")
    return {
        "binding": "http.jsonrpc",
        "exchange": "request_response",
        "family": "response",
        "method": binding.get("method"),
        "anchors": JSONRPC_ANCHORS,
        "completion_fence": "POST_EMIT",
    }


__all__ = ["compile_http_jsonrpc_chain", "compile_http_rest_chain"]
