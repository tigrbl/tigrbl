from __future__ import annotations

import json
from typing import Any, Mapping

from tigrbl_kernel.channel_taxonomy import normalize_exchange
from tigrbl_typing.channel import OpChannel

from ._asgi_jsonrpc import _resolve_jsonrpc_endpoint
from ._asgi_receive import _receive_session_message
from ._asgi_scope import _scheme, build_asgi_channel
from ._asgi_webtransport import (
    _receive_webtransport_session_messages,
    _webtransport_scope_state,
)


async def prepare_channel_context(env: Any, ctx: Any) -> OpChannel:
    temp = ctx.get("temp")
    if not isinstance(temp, dict):
        ctx["temp"] = {}
        temp = ctx["temp"]

    route = temp.setdefault("route", {})
    exchange = str(
        route.get("exchange")
        or getattr(ctx, "tigrbl_exchange", None)
        or "request_response"
    )
    exchange = normalize_exchange(exchange)
    protocol = str(route.get("protocol") or _scheme(getattr(env, "scope", {}) or {}))
    framing = route.get("framing")
    channel = build_asgi_channel(
        env,
        exchange=exchange,
        protocol=protocol or None,
        framing=str(framing) if isinstance(framing, str) else None,
    )
    ctx["channel"] = channel
    ctx["path"] = channel.path
    ctx["method"] = channel.method or channel.protocol.upper()

    dispatch = temp.setdefault("dispatch", {})
    if isinstance(dispatch, dict):
        dispatch.setdefault("channel_protocol", channel.protocol)
        dispatch.setdefault("channel_selector", channel.selector)
        dispatch.setdefault("path_params", dict(channel.path_params))
        endpoint = _resolve_jsonrpc_endpoint(ctx, channel)
        if endpoint:
            dispatch.setdefault("endpoint", endpoint)

    scope = getattr(env, "scope", {}) or {}
    scope_type = str(scope.get("type") or "http")
    if scope_type == "webtransport":
        await _receive_webtransport_session_messages(env, channel, ctx)
        wt_state = _webtransport_scope_state(env)
        trace = wt_state.get("trace")
        if isinstance(trace, list):
            ctx["webtransport_trace"] = trace
            channel.state["webtransport_trace"] = trace
        hook_trace = wt_state.get("hook_trace")
        if isinstance(hook_trace, list):
            ctx["webtransport_hook_trace"] = hook_trace
            channel.state["webtransport_hook_trace"] = hook_trace
        route.setdefault("protocol", dispatch.get("binding_protocol"))
        route.setdefault("selector", channel.path)
        route.setdefault("path_params", dict(channel.path_params))
        route.setdefault("endpoint", dispatch.get("endpoint"))
    elif scope_type == "websocket":
        await _receive_session_message(
            env,
            channel,
            ctx,
            connect_type="websocket.connect",
            receive_type="websocket.receive",
            disconnect_type="websocket.disconnect",
            eager_payload_after_connect=False,
        )
        message = ctx.get("channel_message")
        if isinstance(message, Mapping) and message.get("text") is not None:
            try:
                parsed = json.loads(str(message.get("text")))
            except Exception:
                parsed = None
            if isinstance(parsed, Mapping) and parsed.get("jsonrpc") == "2.0":
                dispatch["binding_protocol"] = (
                    "wss.jsonrpc" if channel.protocol == "wss" else "ws.jsonrpc"
                )
                dispatch["rpc"] = dict(parsed)
                dispatch["rpc_method"] = parsed.get("method")
        route.setdefault("protocol", dispatch.get("binding_protocol"))
        route.setdefault("selector", channel.path)
        route.setdefault("path_params", dict(channel.path_params))
        route.setdefault("endpoint", dispatch.get("endpoint"))

    return channel
