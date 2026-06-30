from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class DirectWebSocketUnary:
    __slots__ = (
        "_receive",
        "_send",
        "_buffered",
        "_buffered_text",
        "_buffered_bytes",
        "_path",
        "_path_params",
        "_scope",
        "accepted",
        "closed",
        "sent_payload",
    )

    def __init__(
        self,
        *,
        receive: Any,
        send: Any,
        path: str,
        path_params: Mapping[str, Any] | None,
        buffered_message: Mapping[str, Any] | None,
    ) -> None:
        self._receive = receive
        self._send = send
        self._buffered = None
        self._buffered_text = None
        self._buffered_bytes = None
        self._path = path
        self._scope = None
        if isinstance(buffered_message, Mapping):
            if buffered_message.get("type") == "websocket.receive":
                text = buffered_message.get("text")
                if isinstance(text, str):
                    self._buffered_text = text
                else:
                    raw = buffered_message.get("bytes")
                    if isinstance(raw, bytes):
                        self._buffered_bytes = raw
                    elif isinstance(raw, bytearray):
                        self._buffered_bytes = bytes(raw)
                    else:
                        self._buffered = (
                            buffered_message
                            if isinstance(buffered_message, dict)
                            else dict(buffered_message)
                        )
            else:
                self._buffered = (
                    buffered_message
                    if isinstance(buffered_message, dict)
                    else dict(buffered_message)
                )
        if isinstance(path_params, dict):
            self._path_params = path_params
        elif path_params:
            self._path_params = dict(path_params)
        else:
            self._path_params = None
        self.accepted = False
        self.closed = False
        self.sent_payload = False

    @property
    def scope(self) -> dict[str, Any]:
        scope = self._scope
        if scope is None:
            scope = {"type": "websocket", "path": self._path}
            self._scope = scope
        return scope

    @property
    def path_params(self) -> dict[str, Any]:
        path_params = self._path_params
        if path_params is None:
            path_params = {}
            self._path_params = path_params
        return path_params

    async def accept(self, subprotocol: str | None = None) -> None:
        if self.accepted:
            return
        if callable(self._send):
            message = {"type": "websocket.accept"}
            if subprotocol is not None:
                message["subprotocol"] = subprotocol
            await self._send(message)
        self.accepted = True

    async def receive(self) -> dict[str, Any]:
        if self._buffered is not None:
            message = self._buffered
            self._buffered = None
            return message
        if callable(self._receive):
            message = await self._receive()
            return (
                dict(message)
                if isinstance(message, Mapping)
                else {"type": "websocket.disconnect", "code": 1006}
            )
        return {"type": "websocket.disconnect", "code": 1006}

    async def receive_text(self) -> str:
        if self._buffered_text is not None:
            text = self._buffered_text
            self._buffered_text = None
            return text
        if self._buffered_bytes is not None:
            raw = self._buffered_bytes
            self._buffered_bytes = None
            return raw.decode("utf-8")
        message = await self.receive()
        if message.get("type") == "websocket.disconnect":
            self.closed = True
            raise RuntimeError("websocket disconnected")
        text = message.get("text")
        if isinstance(text, str):
            return text
        raw = message.get("bytes")
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw).decode("utf-8")
        return ""

    async def send_text(self, data: str) -> None:
        await self.accept()
        if callable(self._send):
            await self._send({"type": "websocket.send", "text": data})
        self.sent_payload = True

    async def send_bytes(self, data: bytes) -> None:
        await self.accept()
        if callable(self._send):
            payload = data if isinstance(data, bytes) else bytes(data)
            await self._send({"type": "websocket.send", "bytes": payload})
        self.sent_payload = True

    async def close(self, code: int = 1000) -> None:
        if self.closed:
            return
        await self.accept()
        if callable(self._send):
            await self._send({"type": "websocket.close", "code": code})
        self.closed = True
