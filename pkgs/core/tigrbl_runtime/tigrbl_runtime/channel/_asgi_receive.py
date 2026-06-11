from __future__ import annotations

from collections import deque
from typing import Any

from tigrbl_typing.channel import OpChannel


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
