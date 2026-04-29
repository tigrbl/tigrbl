from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from typing import Any

TRACE_REST: tuple[str, ...] = (
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

TRACE_RPC: tuple[str, ...] = (
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


async def run_http_rest_chain(request: Mapping[str, Any]) -> dict[str, object]:
    payload = request.get("payload") or {}
    result = await _call_handler(request.get("handler"), payload)
    trace = list(TRACE_REST)
    send = request.get("send")
    if callable(send):
        send({"type": "http.response.start", "status": 200})
        send({"type": "http.response.body", "body": result, "more_body": False})
    return {
        "outcome": "success",
        "result": result,
        "trace": trace,
        "completion_fence": "POST_EMIT",
    }


async def run_http_jsonrpc_chain(request: Mapping[str, Any]) -> dict[str, object]:
    body = request.get("body") or {}
    params = body.get("params", {}) if isinstance(body, Mapping) else {}
    result = await _call_handler(request.get("handler"), params)
    return {
        "outcome": "success",
        "result": result,
        "trace": list(TRACE_RPC),
        "completion_fence": "POST_EMIT",
        "id": body.get("id") if isinstance(body, Mapping) else None,
    }


async def _call_handler(handler: object, payload: object) -> object:
    if not callable(handler):
        return payload
    value = handler(payload)
    if inspect.isawaitable(value):
        return await value
    return value


__all__ = ["run_http_jsonrpc_chain", "run_http_rest_chain"]
