from __future__ import annotations

from typing import Any

from .codec import decode_frame, encode_frame


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


async def decode(ctx: Any) -> Any:
    state = _ws_state(ctx)
    payload = decode_frame("websocket.jsonrpc", state.get("message"))
    state["decoded"] = payload
    return payload


async def encode(ctx: Any) -> Any:
    state = _ws_state(ctx)
    outbound = encode_frame("websocket.jsonrpc", state.get("response"))
    state["outbound"] = outbound
    return outbound


setattr(decode, "__tigrbl_atom_name__", "framing.decode")
setattr(decode, "__tigrbl_label", "atom:framing.decode")
setattr(encode, "__tigrbl_atom_name__", "framing.encode")
setattr(encode, "__tigrbl_label", "atom:framing.encode")


__all__ = ["decode", "encode"]
