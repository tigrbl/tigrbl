from __future__ import annotations

import json
from typing import Any, Mapping
from urllib.parse import parse_qs

from tigrbl_typing.channel import OpChannel


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


def _channel_family(scope_type: str, exchange: str) -> str:
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


async def _receive_websocket_message(env: Any, channel: OpChannel, ctx: Any) -> None:
    receive = getattr(env, "receive", None)
    if not callable(receive):
        return
    message = await receive()
    state = channel.state
    state["last_event"] = message
    if message.get("type") == "websocket.connect":
        state["connected"] = True
        message = await receive()
        state["last_event"] = message
    if message.get("type") == "websocket.receive":
        payload = message.get("bytes")
        if payload is None and message.get("text") is not None:
            payload = str(message.get("text")).encode("utf-8")
        ctx["body"] = payload
        ctx["channel_message"] = message
    elif message.get("type") == "websocket.disconnect":
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
        dispatch.setdefault("binding_protocol", channel.protocol)
        dispatch.setdefault("binding_selector", channel.path)
        dispatch.setdefault("path_params", dict(channel.path_params))

    scope = getattr(env, "scope", {}) or {}
    if str(scope.get("type") or "http") == "websocket":
        await _receive_websocket_message(env, channel, ctx)
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

    return channel


async def _send_websocket_payload(env: Any, payload: Any) -> None:
    send = getattr(env, "send", None)
    if not callable(send):
        return
    await send({"type": "websocket.accept"})
    if payload is not None:
        if isinstance(payload, (bytes, bytearray)):
            await send({"type": "websocket.send", "bytes": bytes(payload)})
        elif isinstance(payload, str):
            await send({"type": "websocket.send", "text": payload})
        else:
            await send(
                {
                    "type": "websocket.send",
                    "text": json.dumps(payload, separators=(",", ":"), default=str),
                }
            )
    await send({"type": "websocket.close", "code": 1000})


async def send_transport_via_channel(env: Any, ctx: Any) -> None:
    scope = getattr(env, "scope", {}) or {}
    scope_type = str(scope.get("type") or "http")
    if scope_type == "websocket":
        temp = getattr(ctx, "temp", None)
        egress = temp.get("egress") if isinstance(temp, dict) else None
        transport = egress.get("transport_response") if isinstance(egress, dict) else None
        payload = None
        if isinstance(transport, Mapping):
            payload = transport.get("body")
        if payload is None:
            payload = getattr(ctx, "result", None)
        await _send_websocket_payload(env, payload)
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
    ctx["transport_completed"] = True
    ctx["current_phase"] = "POST_EMIT"


async def dispatch_legacy_websocket(ctx: Any, route: Any) -> bool:
    channel = ctx.get("channel")
    if channel is None:
        return False
    handler = getattr(route, "handler", None)
    if not callable(handler):
        return False

    class _LegacyWebSocket:
        def __init__(self, op_channel: OpChannel) -> None:
            self.scope = {"type": "websocket", "path": op_channel.path}
            self.path_params = dict(op_channel.path_params)
            self.accepted = False
            self.closed = False
            self._channel = op_channel

        async def accept(self, subprotocol: str | None = None) -> None:
            if callable(self._channel.send):
                message = {"type": "websocket.accept"}
                if subprotocol is not None:
                    message["subprotocol"] = subprotocol
                await self._channel.send(message)
            self.accepted = True

        async def receive(self) -> dict[str, Any]:
            if not callable(self._channel.receive):
                return {"type": "websocket.disconnect", "code": 1006}
            message = await self._channel.receive()
            if message.get("type") == "websocket.disconnect":
                self.closed = True
            return message

        async def receive_text(self) -> str:
            message = await self.receive()
            if message.get("type") == "websocket.disconnect":
                raise RuntimeError("websocket disconnected")
            return str(message.get("text") or "")

        async def send_text(self, data: str) -> None:
            if callable(self._channel.send):
                await self._channel.send({"type": "websocket.send", "text": data})

        async def send_bytes(self, data: bytes) -> None:
            if callable(self._channel.send):
                await self._channel.send({"type": "websocket.send", "bytes": bytes(data)})

        async def close(self, code: int = 1000) -> None:
            if callable(self._channel.send):
                await self._channel.send({"type": "websocket.close", "code": code})
            self.closed = True

    websocket = _LegacyWebSocket(channel)
    result = handler(websocket)
    if hasattr(result, "__await__"):
        await result
    if not websocket.closed:
        if not websocket.accepted:
            await websocket.accept()
        await websocket.close()
    return True
