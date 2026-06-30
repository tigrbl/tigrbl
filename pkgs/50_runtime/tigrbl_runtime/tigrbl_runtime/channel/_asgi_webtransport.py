from __future__ import annotations

import asyncio
from collections import deque
import inspect
from typing import Any, Mapping

from tigrbl_core._spec.hook_spec import HookSpec
from tigrbl_atoms.atoms.transport.asgi_channel import (
    message_payload as _message_payload,
    payload_size as _webtransport_payload_size,
)
from tigrbl_kernel.channel_taxonomy import (
    select_webtransport_hooks,
    webtransport_event_metadata as _webtransport_event_metadata,
)
from tigrbl_kernel.webtransport_events import validate_webtransport_event_payload
from tigrbl_atoms.runtime_channel import WebTransportSessionState
from tigrbl_typing.channel import OpChannel


def _webtransport_scope_state(env: Any) -> dict[str, Any]:
    scope = getattr(env, "scope", {}) or {}
    if not isinstance(scope, dict):
        return {}
    state = scope.setdefault("state", {})
    if not isinstance(state, dict):
        state = {}
        scope["state"] = state
    wt_state = state.setdefault("tigrbl_webtransport", {})
    if not isinstance(wt_state, dict):
        wt_state = {}
        state["tigrbl_webtransport"] = wt_state
    return wt_state


def _webtransport_scope_session_id(env: Any) -> Any:
    scope = getattr(env, "scope", {}) or {}
    if not isinstance(scope, Mapping):
        return None
    if scope.get("session_id") is not None:
        return scope.get("session_id")
    ext = scope.get("ext")
    if isinstance(ext, Mapping):
        wt = ext.get("webtransport")
        if isinstance(wt, Mapping) and wt.get("session_id") is not None:
            return wt.get("session_id")
        unit = ext.get("tigrcorn.unit")
        if isinstance(unit, Mapping) and unit.get("session_id") is not None:
            return unit.get("session_id")
    extensions = scope.get("extensions")
    if isinstance(extensions, Mapping):
        unit = extensions.get("tigrcorn.unit")
        if isinstance(unit, Mapping) and unit.get("session_id") is not None:
            return unit.get("session_id")
    return None


def _enrich_webtransport_message(
    env: Any, message: Mapping[str, Any]
) -> dict[str, Any]:
    enriched = dict(message)
    if enriched.get("session_id") is None:
        session_id = _webtransport_scope_session_id(env)
        if session_id is not None:
            enriched["session_id"] = session_id
    return enriched


def _trace_webtransport_event(
    shared_state: dict[str, Any],
    *,
    direction: str,
    phase: str,
    message: Mapping[str, Any],
) -> None:
    trace = shared_state.setdefault("trace", [])
    if not isinstance(trace, list):
        trace = []
        shared_state["trace"] = trace
    entry: dict[str, Any] = {
        "direction": direction,
        "phase": phase,
        "type": message.get("type"),
    }
    entry.update(
        {
            key: value
            for key, value in _webtransport_event_metadata(
                direction=direction,
                message=message,
            ).items()
            if value is not None
        }
    )
    for key in (
        "session_id",
        "stream_id",
        "stream_direction",
        "datagram_id",
        "framing",
        "more",
        "code",
    ):
        if message.get(key) is not None:
            entry[key] = message.get(key)
    payload_size = _webtransport_payload_size(message)
    if payload_size is not None:
        entry["payload_bytes"] = payload_size
    trace.append(entry)


def _iter_webtransport_hooks(ctx: Any) -> tuple[HookSpec, ...]:
    hooks: list[HookSpec] = []
    seen: set[int] = set()
    for owner_key in ("app", "router"):
        getter = getattr(ctx, "get", None)
        owner = getter(owner_key) if callable(getter) else None
        if owner is None:
            owner = getattr(ctx, owner_key, None)
        for item in _iter_hook_candidates(getattr(owner, "hooks", ())):
            if id(item) in seen:
                continue
            if isinstance(item, HookSpec):
                hooks.append(item)
                seen.add(id(item))
            elif isinstance(item, Mapping):
                hook = HookSpec(**item)
                hooks.append(hook)
                seen.add(id(item))
    return tuple(sorted(hooks, key=lambda hook: int(getattr(hook, "order", 0))))


def _iter_hook_candidates(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        return tuple(value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(value)
    data = getattr(value, "__dict__", None)
    if isinstance(data, Mapping):
        return tuple(data.values())
    return ()


async def _call_webtransport_hook(hook: HookSpec, ctx: Any) -> None:
    fn = hook.fn
    try:
        result = fn(ctx=ctx)
    except TypeError as first_exc:
        try:
            result = fn(ctx)
        except TypeError:
            try:
                result = fn(None, ctx)
            except TypeError:
                raise first_exc
    if inspect.isawaitable(result):
        await result


def _webtransport_context_payload(
    *,
    message: Mapping[str, Any],
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "session_id": message.get("session_id"),
        "stream_id": message.get("stream_id"),
        "stream_direction": message.get("stream_direction"),
        "datagram_id": message.get("datagram_id"),
        "framing": message.get("framing"),
        "lane": metadata.get("lane"),
        "family": metadata.get("family"),
        "exchange": metadata.get("exchange"),
        "event_type": message.get("type"),
        "subevent": metadata.get("subevent"),
        "event": dict(message),
    }


async def _run_webtransport_hooks(
    env: Any,
    ctx: Any,
    *,
    direction: str,
    message: Mapping[str, Any],
) -> None:
    shared_state = _webtransport_scope_state(env)
    metadata = _webtransport_event_metadata(direction=direction, message=message)
    hook_specs = _iter_webtransport_hooks(ctx)
    if hook_specs:
        shared_state["hooks"] = hook_specs
    elif isinstance(shared_state.get("hooks"), tuple):
        hook_specs = shared_state["hooks"]
    hooks = select_webtransport_hooks(
        hook_specs,
        direction=direction,
        metadata=metadata,
    )
    if not hooks:
        return
    hook_trace = shared_state.setdefault("hook_trace", [])
    if not isinstance(hook_trace, list):
        hook_trace = []
        shared_state["hook_trace"] = hook_trace
    webtransport_ctx = _webtransport_context_payload(message=message, metadata=metadata)
    ctx["webtransport"] = webtransport_ctx
    ctx["webtransport_hook_trace"] = hook_trace
    for hook in hooks:
        await _call_webtransport_hook(hook, ctx)
        hook_trace.append(
            {
                "hook": hook.name or getattr(hook.fn, "__name__", repr(hook.fn)),
                "phase": str(getattr(hook.phase, "value", hook.phase)),
                "session_id": message.get("session_id"),
                "stream_id": message.get("stream_id"),
                "datagram_id": message.get("datagram_id"),
                "stream_direction": message.get("stream_direction"),
                "lane": metadata.get("lane"),
                "family": metadata.get("family"),
                "exchange": metadata.get("exchange"),
                "event_type": message.get("type"),
                "subevent": metadata.get("subevent"),
                "framing": message.get("framing"),
            }
        )


async def _receive_webtransport_session_messages(
    env: Any,
    channel: OpChannel,
    ctx: Any,
) -> None:
    receive = getattr(env, "receive", None)
    if not callable(receive):
        return

    state = channel.state
    shared_state = _webtransport_scope_state(env)
    queue: deque[Mapping[str, Any]] = deque()
    session: WebTransportSessionState | None = None

    def _ensure_session(message: Mapping[str, Any]) -> WebTransportSessionState | None:
        nonlocal session
        session_id = message.get("session_id") or _webtransport_scope_session_id(env)
        if session_id is None:
            return session
        state.setdefault("session_id", session_id)
        existing_session = shared_state.get("session")
        if isinstance(
            existing_session, WebTransportSessionState
        ) and existing_session.session_id == str(session_id):
            session = existing_session
        elif session is None:
            session = WebTransportSessionState(session_id=str(session_id))
            shared_state["session"] = session
        state["webtransport_session"] = session
        return session

    async def _record_payload_message(message: Mapping[str, Any]) -> None:
        message = _enrich_webtransport_message(env, message)
        state["last_event"] = message
        shared_state["last_event_type"] = message.get("type")
        _trace_webtransport_event(
            shared_state,
            direction="receive",
            phase="ctx.channel_message",
            message=message,
        )
        message_type = str(message.get("type") or "")
        if message_type.startswith("webtransport.message"):
            raise ValueError("WebTransport message is not a native transport lane")
        current_session = _ensure_session(message)
        if message_type == "webtransport.connect":
            state["connected"] = True
            shared_state["connected"] = True
            await _run_webtransport_hooks(
                env,
                ctx,
                direction="receive",
                message=message,
            )
            return
        if message_type in {
            "webtransport.stream.receive",
            "webtransport.datagram.receive",
        }:
            projection = validate_webtransport_event_payload(
                event=message_type,
                channel="receive",
                payload={**message, "session_id": state.get("session_id")},
            )
            if current_session is not None:
                current_session.apply_event(
                    event=message_type,
                    channel="receive",
                    payload={**message, "session_id": state.get("session_id")},
                    projection=projection,
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
            await _run_webtransport_hooks(
                env,
                ctx,
                direction="receive",
                message=message,
            )
            return
        if message_type == "webtransport.disconnect":
            state["disconnected"] = True
            shared_state["disconnected"] = True
            state["disconnect_event"] = message
            if "channel_message" not in ctx:
                ctx["channel_message"] = message
            await _run_webtransport_hooks(
                env,
                ctx,
                direction="receive",
                message=message,
            )
            return
        ctx["channel_message"] = message

    message = await receive()
    await _record_payload_message(message)
    if message.get("type") == "webtransport.connect":
        if "channel_message" not in ctx:
            message = await receive()
            await _record_payload_message(message)

    while shared_state.get("eager_drain") is True and not state.get("disconnected"):
        try:
            message = await asyncio.wait_for(receive(), timeout=0.001)
        except TimeoutError:
            break
        await _record_payload_message(message)

    state["receive_queue"] = queue
