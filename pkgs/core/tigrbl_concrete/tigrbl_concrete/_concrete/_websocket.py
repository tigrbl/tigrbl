"""Lightweight websocket runtime facade."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WebSocketRoute:
    path_template: str
    pattern: Any
    param_names: tuple[str, ...]
    handler: Any
    name: str
    summary: str | None = None
    description: str | None = None
    tags: list[str] | None = None


class WebSocket:
    def __init__(self, scope: dict[str, Any], receive: Any, send: Any, *, path_params: dict[str, str] | None = None) -> None:
        self.scope = scope
        self._receive = receive
        self._send = send
        self.path_params = path_params or {}
        self.accepted = False
        self.closed = False

    async def accept(self, subprotocol: str | None = None) -> None:
        message = {"type": "websocket.accept"}
        if subprotocol is not None:
            message["subprotocol"] = subprotocol
        await self._send(message)
        self.accepted = True

    async def receive(self) -> dict[str, Any]:
        return await self._receive()

    async def receive_text(self) -> str:
        message = await self.receive()
        if message.get("type") == "websocket.disconnect":
            self.closed = True
            raise RuntimeError("websocket disconnected")
        return str(message.get("text") or "")

    async def send_text(self, data: str) -> None:
        await self._send({"type": "websocket.send", "text": data})

    async def send_bytes(self, data: bytes) -> None:
        await self._send({"type": "websocket.send", "bytes": bytes(data)})

    async def close(self, code: int = 1000) -> None:
        await self._send({"type": "websocket.close", "code": code})
        self.closed = True


__all__ = ["WebSocket", "WebSocketRoute"]
