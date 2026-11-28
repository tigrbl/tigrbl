from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def _ctx_get(ctx: Any, key: str, default: Any = None) -> Any:
    getter = getattr(ctx, "get", None)
    if callable(getter):
        try:
            return getter(key, default)
        except Exception:
            pass
    return getattr(ctx, key, default)


def _ctx_set(ctx: Any, key: str, value: Any) -> None:
    try:
        ctx[key] = value
        return
    except Exception:
        pass
    setattr(ctx, key, value)


def _temp(ctx: Any) -> dict[str, Any]:
    temp = _ctx_get(ctx, "temp")
    if not isinstance(temp, dict):
        temp = {}
        _ctx_set(ctx, "temp", temp)
    return temp


def _ws_state(ctx: Any) -> dict[str, Any]:
    return _temp(ctx).setdefault("websocket", {})


def _channel(ctx: Any) -> Any:
    channel = _ctx_get(ctx, "channel")
    if channel is None:
        raise RuntimeError("websocket transport atom requires channel context")
    return channel


async def accept(ctx: Any, *, subprotocol: str | None = None) -> None:
    channel = _channel(ctx)
    send = getattr(channel, "send", None)
    if callable(send):
        message: dict[str, Any] = {"type": "websocket.accept"}
        if subprotocol is not None:
            message["subprotocol"] = subprotocol
        await send(message)
    state = _ws_state(ctx)
    state["accepted"] = True
    state["selected_subprotocol"] = subprotocol


async def receive(ctx: Any) -> dict[str, Any]:
    channel = _channel(ctx)
    recv = getattr(channel, "receive", None)
    if not callable(recv):
        message = {"type": "websocket.disconnect", "code": 1006}
    else:
        message = await recv()
        if not isinstance(message, Mapping):
            message = {"type": "websocket.disconnect", "code": 1006}
        else:
            message = dict(message)
    while message.get("type") == "websocket.connect" and callable(recv):
        message = await recv()
        if not isinstance(message, Mapping):
            message = {"type": "websocket.disconnect", "code": 1006}
            break
        message = dict(message)
    state = _ws_state(ctx)
    state["message"] = message
    state["disconnected"] = message.get("type") == "websocket.disconnect"
    return message


async def emit(ctx: Any) -> None:
    channel = _channel(ctx)
    send = getattr(channel, "send", None)
    if not callable(send):
        return
    message = _ws_state(ctx).get("outbound")
    if isinstance(message, Mapping):
        await send(dict(message))
        _ws_state(ctx)["emitted"] = True


async def close(ctx: Any, *, code: int = 1000) -> None:
    channel = _channel(ctx)
    send = getattr(channel, "send", None)
    state = _ws_state(ctx)
    if callable(send) and not state.get("disconnected"):
        await send({"type": "websocket.close", "code": code})
    state["closed"] = True
    state["disconnected"] = True


for _name, _fn in {
    "transport.accept": accept,
    "transport.receive": receive,
    "transport.emit": emit,
    "transport.close": close,
}.items():
    setattr(_fn, "__tigrbl_atom_name__", _name)
    setattr(_fn, "__tigrbl_label", f"atom:{_name}")


__all__ = ["accept", "receive", "emit", "close"]
