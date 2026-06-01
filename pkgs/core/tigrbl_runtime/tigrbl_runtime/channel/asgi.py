from __future__ import annotations

import asyncio
from collections import deque
import json
from typing import Any, Mapping
from urllib.parse import parse_qs

from tigrbl_core.config.constants import (
    __JSONRPC_DEFAULT_ENDPOINT__,
    __JSONRPC_DEFAULT_ENDPOINT_MAPPINGS__,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload
from tigrbl_runtime.protocol.webtransport_session import WebTransportSessionState
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
    receive_type: str | tuple[str, ...],
    disconnect_type: str,
    eager_payload_after_connect: bool = True,
) -> None:
    receive = getattr(env, "receive", None)
    if not callable(receive):
        return
    message = await receive()
    state = channel.state
    state["last_event"] = message
    if message.get("type") == connect_type:
        state["connected"] = True
        if message.get("session_id") is not None:
            state["session_id"] = message.get("session_id")
        if not eager_payload_after_connect:
            ctx["channel_message"] = message
            return
        message = await receive()
        state["last_event"] = message
    receive_types = (receive_type,) if isinstance(receive_type, str) else receive_type
    if message.get("type") in receive_types:
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
        if payload is None:
            payload = message.get("data")
        if payload is None and message.get("text") is not None:
            payload = str(message.get("text")).encode("utf-8")
        ctx["body"] = payload
        ctx["channel_message"] = message
        for key in (
            "session_id",
            "stream_id",
            "stream_direction",
            "datagram_id",
            "framing",
        ):
            if message.get(key) is not None:
                state[key] = message.get(key)
    elif message.get("type") == disconnect_type:
        state["disconnected"] = True
        ctx["channel_message"] = message


def _message_payload(message: Mapping[str, Any]) -> Any:
    payload = message.get("bytes")
    if payload is None:
        payload = message.get("data")
    if payload is None and message.get("text") is not None:
        payload = str(message.get("text")).encode("utf-8")
    return payload


async def _receive_webtransport_session_messages(
    env: Any,
    channel: OpChannel,
    ctx: Any,
) -> None:
    receive = getattr(env, "receive", None)
    if not callable(receive):
        return

    state = channel.state
    queue: deque[Mapping[str, Any]] = deque()
    message = await receive()
    state["last_event"] = message
    if str(message.get("type") or "").startswith("webtransport.message"):
        raise ValueError("WebTransport message is not a native transport lane")

    session_id = message.get("session_id")
    session: WebTransportSessionState | None = None
    if session_id is not None:
        session = WebTransportSessionState(session_id=str(session_id))
        state["session_id"] = session_id
        state["webtransport_session"] = session

    if message.get("type") == "webtransport.connect":
        state["connected"] = True
    elif message.get("type") == "webtransport.disconnect":
        state["disconnected"] = True
        ctx["channel_message"] = message
        return
    else:
        queue.append(message)

    while True:
        if queue:
            try:
                message = await asyncio.wait_for(receive(), timeout=0.001)
            except TimeoutError:
                break
        else:
            message = await receive()
        state["last_event"] = message
        message_type = str(message.get("type") or "")
        if message_type.startswith("webtransport.message"):
            raise ValueError("WebTransport message is not a native transport lane")
        if message.get("session_id") is not None:
            state.setdefault("session_id", message.get("session_id"))
            if session is None:
                session = WebTransportSessionState(session_id=str(message.get("session_id")))
                state["webtransport_session"] = session
        if message_type in {"webtransport.stream.receive", "webtransport.datagram.receive"}:
            validate_webtransport_event_payload(
                event=message_type,
                channel="receive",
                payload={**message, "session_id": state.get("session_id")},
            )
            if session is not None:
                session.apply_event(
                    event=message_type,
                    channel="receive",
                    payload={**message, "session_id": state.get("session_id")},
                )
            queue.append(message)
            for key in (
                "session_id",
                "stream_id",
                "stream_direction",
                "datagram_id",
                "framing",
            ):
                if message.get(key) is not None:
                    state[key] = message.get(key)
            if "body" not in ctx:
                ctx["body"] = _message_payload(message)
            ctx["channel_message"] = message
            continue
        if message_type == "webtransport.disconnect":
            state["disconnected"] = True
            state["disconnect_event"] = message
            if "channel_message" not in ctx:
                ctx["channel_message"] = message
            break
        ctx["channel_message"] = message
        break

    state["receive_queue"] = queue


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
        if (
            isinstance(message, Mapping)
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


def _webtransport_payload_event(
    *,
    base: Mapping[str, Any],
    payload: Any,
) -> dict[str, Any]:
    event_type = str(base.get("type") or "")
    session_id = base.get("session_id")
    if event_type == "webtransport.stream.receive":
        out: dict[str, Any] = {
            "type": "webtransport.stream.send",
            "session_id": session_id,
            "stream_id": base.get("stream_id"),
            "stream_direction": base.get("stream_direction", "bidi"),
        }
        if base.get("framing") is not None:
            out["framing"] = base.get("framing")
        if isinstance(payload, (bytes, bytearray)):
            out["data"] = bytes(payload)
        elif isinstance(payload, str):
            out["data"] = payload.encode("utf-8")
        else:
            out["data"] = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
        out["more"] = False
        return out
    if event_type == "webtransport.datagram.receive":
        out = {
            "type": "webtransport.datagram.send",
            "session_id": session_id,
            "datagram_id": base.get("datagram_id"),
        }
        if base.get("framing") is not None:
            out["framing"] = base.get("framing")
        if isinstance(payload, (bytes, bytearray)):
            out["data"] = bytes(payload)
        elif isinstance(payload, str):
            out["data"] = payload.encode("utf-8")
        else:
            out["data"] = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
        return out
    out = {"type": "webtransport.send", "session_id": session_id}
    if isinstance(payload, (bytes, bytearray)):
        out["bytes"] = bytes(payload)
    elif isinstance(payload, str):
        out["text"] = payload
    else:
        out["text"] = json.dumps(payload, separators=(",", ":"), default=str)
    return out


def _coerce_webtransport_stream_id(value: Any, *, fallback: int) -> Any:
    if value is None or value == "":
        return fallback
    return value


def _row_for_lane(rows: Any, *, lane_id: Any, index: int) -> Mapping[str, Any]:
    if not isinstance(rows, list) or not rows:
        return {}
    for row in rows:
        if isinstance(row, Mapping) and str(row.get("id") or "") == str(lane_id):
            return row
    if index < len(rows) and isinstance(rows[index], Mapping):
        return rows[index]
    return {}


def _webtransport_structured_payload_events(
    *,
    session_id: Any,
    inbound: Mapping[str, Any] | list[Mapping[str, Any]],
    payload: Mapping[str, Any],
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    inbound_events = inbound if isinstance(inbound, list) else [inbound]
    bidi_index = 0
    for current in inbound_events:
        inbound_type = str(current.get("type") or "")
        inbound_stream_id = _coerce_webtransport_stream_id(
            current.get("stream_id"),
            fallback=4 + bidi_index,
        )
        inbound_direction = str(current.get("stream_direction") or "bidi")
        framing = current.get("framing")

        if inbound_type == "webtransport.stream.receive" and inbound_direction == "bidi":
            row = _row_for_lane(
                payload.get("bidirectional_streams"),
                lane_id=inbound_stream_id,
                index=bidi_index,
            )
            bidi_index += 1
            message = row.get("message") if isinstance(row, Mapping) else None
            if message is None:
                message = payload.get("message")
            if message is None:
                message = "demo-bidirectional"
            event: dict[str, Any] = {
                "type": "webtransport.stream.send",
                "session_id": session_id,
                "stream_id": inbound_stream_id,
                "stream_direction": "bidi",
                "data": str(message).encode("utf-8"),
                "more": False,
            }
            if framing is not None:
                event["framing"] = framing
            events.append(event)

    first_inbound_stream_id = next(
        (
            item.get("stream_id")
            for item in inbound_events
            if str(item.get("type") or "") == "webtransport.stream.receive"
        ),
        None,
    )
    numeric_stream_base: int | None = None
    try:
        numeric_stream_base = int(first_inbound_stream_id)
    except Exception:
        numeric_stream_base = None

    uni_rows = payload.get("unidirectional_streams")
    if isinstance(uni_rows, list):
        for index, row in enumerate(uni_rows):
            if not isinstance(row, Mapping):
                continue
            message = row.get("message")
            if message is None:
                continue
            stream_id: Any = row.get("id") or f"server-stream-{index + 1}"
            if numeric_stream_base is not None:
                try:
                    stream_id = int(stream_id)
                except Exception:
                    stream_id = numeric_stream_base + index + 1
            event = {
                "type": "webtransport.stream.send",
                "session_id": session_id,
                "stream_id": stream_id,
                "stream_direction": "server_to_client",
                "data": str(message).encode("utf-8"),
                "more": False,
            }
            row_framing = row.get("framing") if isinstance(row, Mapping) else None
            if row_framing is not None:
                event["framing"] = row_framing
            events.append(event)

    datagram_rows = payload.get("datagrams")
    inbound_datagram_ids = [
        item.get("datagram_id")
        for item in inbound_events
        if str(item.get("type") or "") == "webtransport.datagram.receive"
        and item.get("datagram_id") is not None
    ]
    inbound_datagram_framings = [
        item.get("framing")
        for item in inbound_events
        if str(item.get("type") or "") == "webtransport.datagram.receive"
        and item.get("framing") is not None
    ]
    if isinstance(datagram_rows, list):
        for index, row in enumerate(datagram_rows):
            if not isinstance(row, Mapping):
                continue
            if str(row.get("direction") or "") == "client-to-server":
                continue
            body = row.get("payload")
            if body is None:
                continue
            event = {
                "type": "webtransport.datagram.send",
                "session_id": session_id,
                "datagram_id": str(
                    row.get("id")
                    or (inbound_datagram_ids[index] if index < len(inbound_datagram_ids) else None)
                    or f"datagram-{index + 1}"
                ),
                "data": str(body).encode("utf-8"),
            }
            row_framing = row.get("framing") if isinstance(row, Mapping) else None
            if row_framing is None and index < len(inbound_datagram_framings):
                row_framing = inbound_datagram_framings[index]
            if row_framing is not None:
                event["framing"] = row_framing
            events.append(event)
    return events


async def _send_webtransport_payload(env: Any, ctx: Any, payload: Any) -> None:
    send = getattr(env, "send", None)
    if not callable(send):
        return
    channel = ctx.get("channel")
    state = getattr(channel, "state", None) if channel is not None else None
    message = ctx.get("channel_message")
    if not isinstance(message, Mapping):
        message = {}
    queue: list[Mapping[str, Any]] = []
    if isinstance(state, dict):
        raw_queue = state.get("receive_queue")
        if isinstance(raw_queue, deque):
            queue = [item for item in raw_queue if isinstance(item, Mapping)]
        elif isinstance(raw_queue, list):
            queue = [item for item in raw_queue if isinstance(item, Mapping)]
    session_id = None
    if isinstance(state, dict):
        session_id = state.get("session_id")
    session_id = message.get("session_id") or session_id
    message_type = str(message.get("type") or "")
    if message_type == "webtransport.disconnect":
        close: dict[str, Any] = {
            "type": "webtransport.close",
            "code": int(message.get("code") or 1000),
        }
        if session_id is not None:
            close["session_id"] = session_id
        await send(close)
        return
    structured_payload = isinstance(payload, Mapping) and any(
        key in payload for key in ("bidirectional_streams", "unidirectional_streams", "datagrams")
    )
    if structured_payload:
        if not queue and message_type in {"webtransport.stream.receive", "webtransport.datagram.receive"}:
            queue = [message]
        if not queue:
            raise ValueError(
                "structured WebTransport payloads require inbound stream.receive or datagram.receive events"
            )
        for item in queue:
            item_type = str(item.get("type") or "")
            validate_webtransport_event_payload(
                event=item_type,
                channel="receive",
                payload={**item, "session_id": session_id},
            )
    accept: dict[str, Any] = {"type": "webtransport.accept"}
    if session_id is not None:
        accept["session_id"] = session_id
    await send(accept)
    session = state.get("webtransport_session") if isinstance(state, dict) else None
    if isinstance(session, WebTransportSessionState):
        session.apply_event(event="webtransport.accept", channel="send", payload={"session_id": session_id})
    if payload is not None:
        base = {**message, "session_id": session_id}
        if structured_payload:
            for event in _webtransport_structured_payload_events(
                session_id=session_id,
                inbound=[{**item, "session_id": session_id} for item in queue],
                payload=payload,
            ):
                if isinstance(session, WebTransportSessionState):
                    session.apply_event(
                        event=str(event.get("type")),
                        channel="send",
                        payload=dict(event),
                    )
                await send(event)
        else:
            event = _webtransport_payload_event(base=base, payload=payload)
            if isinstance(session, WebTransportSessionState):
                session.apply_event(
                    event=str(event.get("type")),
                    channel="send",
                    payload=dict(event),
                )
            await send(event)
    close: dict[str, Any] = {"type": "webtransport.close", "code": 1000}
    if session_id is not None:
        close["session_id"] = session_id
    if isinstance(session, WebTransportSessionState):
        session.apply_event(event="webtransport.close", channel="send", payload=close)
    await send(close)


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
        if scope_type == "webtransport":
            await _send_webtransport_payload(env, ctx, payload)
        else:
            await _send_session_payload(
                env,
                payload,
                accept_type="websocket.accept",
                send_type="websocket.send",
                close_type="websocket.close",
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
