from __future__ import annotations

from typing import Any

from tigrbl_atoms.atoms.transport.asgi_channel import (
    complete_channel_state as _complete_channel_state,
)
from tigrbl_typing.channel import OpChannel

from ._asgi_scope import build_asgi_channel
from ._asgi_send import send_transport_via_channel
from .websocket import RuntimeWebSocket


def channel_senders():
    from tigrbl_atoms.atoms.egress.asgi_send import _send_json

    return _send_json, send_transport_via_channel


async def complete_channel(env: Any, ctx: Any) -> None:
    channel = ctx.get("channel")
    if channel is None:
        channel = build_asgi_channel(env)
        ctx["channel"] = channel
    if isinstance(getattr(channel, "state", None), dict):
        _complete_channel_state(channel.state)
    ctx["transport_completed"] = True
    ctx["current_phase"] = "POST_EMIT"


def websocket_adapter(channel: OpChannel) -> RuntimeWebSocket:
    return RuntimeWebSocket(channel)
