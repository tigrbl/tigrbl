from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tigrbl_typing.channel import OpChannel


@dataclass(frozen=True)
class RuntimeWebSocketRoute:
    path_template: str
    pattern: Any
    param_names: tuple[str, ...]
    handler: Any
    name: str
    protocol: str = "ws"
    exchange: str = "bidirectional_stream"
    framing: str = "text"
    summary: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class RuntimeWebSocket:
    def __init__(self, channel: OpChannel) -> None:
        self.scope = {"type": "websocket", "path": channel.path}
        self.path_params = dict(channel.path_params)
        self.accepted = False
        self.closed = False
        self._channel = channel

    def _state(self) -> dict[str, Any]:
        state = getattr(self._channel, "state", None)
        if not isinstance(state, dict):
            state = {}
            self._channel.state = state
        return state

    async def accept(self, subprotocol: str | None = None) -> None:
        if callable(self._channel.send):
            message = {"type": "websocket.accept"}
            if subprotocol is not None:
                message["subprotocol"] = subprotocol
            await self._channel.send(message)
        self.accepted = True
        state = self._state()
        state["accepted"] = True
        state["transport_sent"] = True

    async def receive(self) -> dict[str, Any]:
        state = self._state()
        queue = state.get("receive_queue")
        if isinstance(queue, list) and queue:
            message = queue.pop(0)
        elif callable(self._channel.receive):
            message = await self._channel.receive()
        else:
            message = {"type": "websocket.disconnect", "code": 1006}
        state["last_event"] = message
        if message.get("type") == "websocket.disconnect":
            self.closed = True
            state["disconnected"] = True
        return message

    async def receive_text(self) -> str:
        message = await self.receive()
        if message.get("type") == "websocket.disconnect":
            raise RuntimeError("websocket disconnected")
        return str(message.get("text") or "")

    async def send_text(self, data: str) -> None:
        if callable(self._channel.send):
            await self._channel.send({"type": "websocket.send", "text": data})
        state = self._state()
        state["emitted"] = True
        state["transport_sent"] = True

    async def send_bytes(self, data: bytes) -> None:
        if callable(self._channel.send):
            await self._channel.send({"type": "websocket.send", "bytes": bytes(data)})
        state = self._state()
        state["emitted"] = True
        state["transport_sent"] = True

    async def close(self, code: int = 1000) -> None:
        if callable(self._channel.send):
            await self._channel.send({"type": "websocket.close", "code": code})
        self.closed = True
        state = self._state()
        state["closed"] = True
        state["disconnected"] = True
        state["transport_sent"] = True


__all__ = ["RuntimeWebSocket", "RuntimeWebSocketRoute"]
