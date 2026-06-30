from __future__ import annotations

from collections import deque
from typing import Any, Mapping

from tigrbl_atoms.atoms.transport.asgi_channel import (
    session_payload_events as _session_payload_events,
    webtransport_payload_event as _webtransport_payload_event,
    webtransport_structured_payload_events as _webtransport_structured_payload_events,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload
from tigrbl_atoms.runtime_channel import WebTransportSessionState

from ._asgi_webtransport import (
    _run_webtransport_hooks,
    _trace_webtransport_event,
    _webtransport_scope_session_id,
    _webtransport_scope_state,
)


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
    for event in _session_payload_events(
        payload,
        accept_type=accept_type,
        send_type=send_type,
        close_type=close_type,
    ):
        await send(event)


async def _send_webtransport_payload(env: Any, ctx: Any, payload: Any) -> None:
    send = getattr(env, "send", None)
    if not callable(send):
        return
    shared_state = _webtransport_scope_state(env)
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
    session_id = (
        message.get("session_id") or session_id or _webtransport_scope_session_id(env)
    )
    message_type = str(message.get("type") or "")
    if message_type == "webtransport.disconnect":
        if shared_state.get("closed") is True:
            return
        close: dict[str, Any] = {
            "type": "webtransport.close",
            "code": int(message.get("code") or 1000),
        }
        if session_id is not None:
            close["session_id"] = session_id
        _trace_webtransport_event(
            shared_state,
            direction="send",
            phase="transport.close",
            message=close,
        )
        await _run_webtransport_hooks(env, ctx, direction="send", message=close)
        await send(close)
        shared_state["closed"] = True
        return
    structured_payload = isinstance(payload, Mapping) and any(
        key in payload
        for key in ("bidirectional_streams", "unidirectional_streams", "datagrams")
    )
    if structured_payload:
        if not queue and message_type in {
            "webtransport.stream.receive",
            "webtransport.datagram.receive",
        }:
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
    session = state.get("webtransport_session") if isinstance(state, dict) else None
    if shared_state.get("accepted") is not True:
        _trace_webtransport_event(
            shared_state,
            direction="send",
            phase="transport.accept",
            message=accept,
        )
        await _run_webtransport_hooks(env, ctx, direction="send", message=accept)
        await send(accept)
        shared_state["accepted"] = True
        if isinstance(session, WebTransportSessionState):
            session.apply_event(
                event="webtransport.accept",
                channel="send",
                payload={"session_id": session_id},
            )
    if payload is not None:
        base = {**message, "session_id": session_id}
        if structured_payload:
            for event in _webtransport_structured_payload_events(
                session_id=session_id,
                inbound=[{**item, "session_id": session_id} for item in queue],
                payload=payload,
            ):
                if isinstance(session, WebTransportSessionState):
                    projection = validate_webtransport_event_payload(
                        event=str(event.get("type")),
                        channel="send",
                        payload=dict(event),
                    )
                    session.apply_event(
                        event=str(event.get("type")),
                        channel="send",
                        payload=dict(event),
                        projection=projection,
                    )
                _trace_webtransport_event(
                    shared_state,
                    direction="send",
                    phase="transport.emit",
                    message=event,
                )
                await _run_webtransport_hooks(env, ctx, direction="send", message=event)
                await send(event)
        else:
            event = _webtransport_payload_event(base=base, payload=payload)
            if isinstance(session, WebTransportSessionState):
                projection = validate_webtransport_event_payload(
                    event=str(event.get("type")),
                    channel="send",
                    payload=dict(event),
                )
                session.apply_event(
                    event=str(event.get("type")),
                    channel="send",
                    payload=dict(event),
                    projection=projection,
                )
            _trace_webtransport_event(
                shared_state,
                direction="send",
                phase="transport.emit",
                message=event,
            )
            await _run_webtransport_hooks(env, ctx, direction="send", message=event)
            await send(event)
    close_after_response = bool(
        shared_state.get("close_after_response") or shared_state.get("disconnected")
    )
    if close_after_response:
        close: dict[str, Any] = {"type": "webtransport.close", "code": 1000}
        disconnect_event = (
            state.get("disconnect_event") if isinstance(state, dict) else None
        )
        if isinstance(disconnect_event, Mapping):
            close["code"] = int(disconnect_event.get("code") or 1000)
        if session_id is not None:
            close["session_id"] = session_id
        if isinstance(session, WebTransportSessionState):
            session.apply_event(
                event="webtransport.close", channel="send", payload=close
            )
        _trace_webtransport_event(
            shared_state,
            direction="send",
            phase="transport.close",
            message=close,
        )
        await _run_webtransport_hooks(env, ctx, direction="send", message=close)
        await send(close)
        shared_state["closed"] = True


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
        transport = (
            egress.get("transport_response") if isinstance(egress, dict) else None
        )
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
