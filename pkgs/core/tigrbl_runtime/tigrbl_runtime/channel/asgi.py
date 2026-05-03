from __future__ import annotations

from collections import deque
import json
from typing import Any, Mapping
from urllib.parse import parse_qs

from tigrbl_core.config.constants import (
    __JSONRPC_DEFAULT_ENDPOINT__,
    __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__,
)
from tigrbl_typing.channel import OpChannel

from .websocket import RuntimeWebSocket


def _headers(scope: Mapping[str, Any]) -> dict[str, str]:
    pairs = scope.get("headers", ())
    out: dict[str, str] = {}
    for key, value in pairs or ():
        try:
            out[bytes(key).decode("latin-1").lower()] = bytes(value).decode("latin-1")
        except Exception:
            continue
    return out


def _query(scope: Mapping[str, Any]) -> dict[str, list[str]]:
    raw = scope.get("query_string", b"")
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    if not isinstance(raw, (bytes, bytearray)):
        return {}
    return {
        key: [str(item) for item in values]
        for key, values in parse_qs(bytes(raw).decode("utf-8"), keep_blank_values=True).items()
    }


def _scheme(scope: Mapping[str, Any]) -> str:
    return str(scope.get("scheme") or "").lower()


def normalize_exchange(exchange: str | None) -> str:
    token = str(exchange or "request_response")
    if token == "bidirectional":
        return "bidirectional_stream"
    return token


def _channel_family(scope_type: str, exchange: str) -> str:
    exchange = normalize_exchange(exchange)
    if scope_type == "websocket":
        return "socket"
    if scope_type == "webtransport":
        return "session"
    if exchange in {"server_stream", "bidirectional_stream"}:
        return "stream"
    if exchange == "fire_and_forget":
        return "request"
    return "response"


def _channel_kind(scope_type: str, exchange: str) -> str:
    exchange = normalize_exchange(exchange)
    if scope_type == "websocket":
        return "websocket"
    if scope_type == "webtransport":
        return "webtransport"
    if exchange == "server_stream":
        return "stream"
    if exchange == "event_stream":
        return "sse"
    return "http"


def _subevents(scope_type: str, exchange: str) -> tuple[str, ...]:
    exchange = normalize_exchange(exchange)
    if scope_type == "websocket":
        return ("connect", "receive", "emit", "complete", "disconnect")
    if scope_type == "webtransport":
        return ("connect", "receive", "emit", "complete", "disconnect")
    if exchange in {"server_stream", "bidirectional_stream", "event_stream"}:
        return ("receive", "emit", "complete")
    return ("receive", "emit", "complete")


def build_asgi_channel(
    env: Any,
    *,
    exchange: str = "request_response",
    protocol: str | None = None,
    framing: str | None = None,
) -> OpChannel:
    exchange = normalize_exchange(exchange)
    scope = getattr(env, "scope", {}) or {}
    scope_type = str(scope.get("type") or "http")
    path = str(scope.get("path") or "/")
    method = scope.get("method")
    protocol_name = protocol or _scheme(scope) or scope_type
    selector = path
    if scope_type == "http" and isinstance(method, str):
        selector = f"{method.upper()} {path}"
    return OpChannel(
        kind=_channel_kind(scope_type, exchange),
        family=_channel_family(scope_type, exchange),
        exchange=exchange,
        protocol=protocol_name,
        path=path,
        method=str(method).upper() if isinstance(method, str) else None,
        selector=selector,
        framing=framing,
        subevents=_subevents(scope_type, exchange),
        headers=_headers(scope),
        query=_query(scope),
        path_params=scope.get("path_params", {}) or {},
        send=getattr(env, "send", None),
        receive=getattr(env, "receive", None),
    )


def _normalize_path(path: str) -> str:
    return path.rstrip("/") or "/"


def _resolve_jsonrpc_endpoint(ctx: Any, channel: OpChannel) -> str | None:
    if channel.kind != "http" or str(channel.method or "").upper() != "POST":
        return None

    path = _normalize_path(channel.path)
    route = {}
    temp = ctx.get("temp")
    if isinstance(temp, dict):
        route = temp.setdefault("route", {})
    if isinstance(route, Mapping):
        endpoint = route.get("endpoint")
        if isinstance(endpoint, str) and endpoint:
            return endpoint

    for owner_key in ("router", "app"):
        owner = ctx.get(owner_key)
        mounts = getattr(owner, "_jsonrpc_endpoint_mounts", None)
        if isinstance(mounts, Mapping):
            endpoint = mounts.get(path) or mounts.get(channel.path)
            if isinstance(endpoint, str) and endpoint:
                return endpoint

    for endpoint, mapped_path in __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__.items():
        if path == _normalize_path(mapped_path):
            return endpoint
    return None


async def _receive_session_message(
    env: Any,
    channel: OpChannel,
    ctx: Any,
    *,
    connect_type: str,
    receive_type: str,
    disconnect_type: str,
) -> None:
    receive = getattr(env, "receive", None)
    if not callable(receive):
        return
    message = await receive()
    state = channel.state
    state["last_event"] = message
    if message.get("type") == connect_type:
        state["connected"] = True
        message = await receive()
        state["last_event"] = message
    if message.get("type") == receive_type:
        queue = state.get("receive_queue")
        if isinstance(queue, deque):
            queue.append(message)
        else:
            next_queue = deque()
            if isinstance(queue, list):
                next_queue.extend(queue)
            next_queue.append(message)
            state["receive_queue"] = next_queue
        payload = message.get("bytes")
        if payload is None and message.get("text") is not None:
            payload = str(message.get("text")).encode("utf-8")
        ctx["body"] = payload
        ctx["channel_message"] = message
    elif message.get("type") == disconnect_type:
        state["disconnected"] = True
        ctx["channel_message"] = message


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
    if scope_type in {"websocket", "webtransport"}:
        await _receive_session_message(
            env,
            channel,
            ctx,
            connect_type=(
                "websocket.connect"
                if scope_type == "websocket"
                else "webtransport.connect"
            ),
            receive_type=(
                "websocket.receive"
                if scope_type == "websocket"
                else "webtransport.receive"
            ),
            disconnect_type=(
                "websocket.disconnect"
                if scope_type == "websocket"
                else "webtransport.disconnect"
            ),
        )
        message = ctx.get("channel_message")
        if (
            scope_type == "websocket"
            and isinstance(message, Mapping)
            and message.get("text") is not None
        ):
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


async def _send_session_payload(
    env: Any,
    payload: Any,
    *,
    accept_type: str,
    send_type: str,
    close_type: str,
) -> None:
    send = getattr(env, "send", None)
    if not callable(send):
        return
    await send({"type": accept_type})
    if payload is not None:
        if isinstance(payload, (bytes, bytearray)):
            await send({"type": send_type, "bytes": bytes(payload)})
        elif isinstance(payload, str):
            await send({"type": send_type, "text": payload})
        else:
            await send(
                {
                    "type": send_type,
                    "text": json.dumps(payload, separators=(",", ":"), default=str),
                }
            )
    await send({"type": close_type, "code": 1000})


async def send_transport_via_channel(env: Any, ctx: Any) -> None:
    scope = getattr(env, "scope", {}) or {}
    scope_type = str(scope.get("type") or "http")
    if scope_type in {"websocket", "webtransport"}:
        channel = ctx.get("channel")
        state = getattr(channel, "state", None) if channel is not None else None
        if isinstance(state, dict) and state.get("transport_sent") is True:
            temp = getattr(ctx, "temp", None)
            if isinstance(temp, dict):
                temp.setdefault("egress", {})["response_sent"] = True
            return
        temp = getattr(ctx, "temp", None)
        egress = temp.get("egress") if isinstance(temp, dict) else None
        transport = egress.get("transport_response") if isinstance(egress, dict) else None
        payload = None
        if isinstance(transport, Mapping):
            payload = transport.get("body")
        if payload is None:
            payload = getattr(ctx, "result", None)
        await _send_session_payload(
            env,
            payload,
            accept_type=(
                "websocket.accept"
                if scope_type == "websocket"
                else "webtransport.accept"
            ),
            send_type=(
                "websocket.send"
                if scope_type == "websocket"
                else "webtransport.send"
            ),
            close_type=(
                "websocket.close"
                if scope_type == "websocket"
                else "webtransport.close"
            ),
        )
        if isinstance(state, dict):
            state["transport_sent"] = True
            state["emitted"] = payload is not None
        if isinstance(egress, dict):
            egress["response_sent"] = True
        return
    from tigrbl_atoms.atoms.egress.asgi_send import _send_transport_response

    await _send_transport_response(env, ctx)


def channel_senders():
    from tigrbl_atoms.atoms.egress.asgi_send import _send_json

    return _send_json, send_transport_via_channel


async def complete_channel(env: Any, ctx: Any) -> None:
    channel = ctx.get("channel")
    if channel is None:
        channel = build_asgi_channel(env)
        ctx["channel"] = channel
    if isinstance(getattr(channel, "state", None), dict):
        channel.state["completed"] = True
        channel.state["completion_fence"] = "POST_EMIT"
    ctx["transport_completed"] = True
    ctx["current_phase"] = "POST_EMIT"


def websocket_adapter(channel: OpChannel) -> RuntimeWebSocket:
    return RuntimeWebSocket(channel)
