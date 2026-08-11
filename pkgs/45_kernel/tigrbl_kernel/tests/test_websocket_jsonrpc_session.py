from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_kernel.protocol_chains.websocket import (
    build_websocket_jsonrpc_session_handler,
)


@pytest.mark.asyncio
async def test_jsonrpc_session_marks_transport_as_owned_after_accept() -> None:
    inbound = [
        {"type": "websocket.connect"},
        {"type": "websocket.disconnect", "code": 1000},
    ]
    sent: list[dict] = []

    async def receive() -> dict:
        return inbound.pop(0)

    async def send(message: dict) -> None:
        sent.append(message)

    channel = SimpleNamespace(receive=receive, send=send, state={})
    handler = build_websocket_jsonrpc_session_handler(SimpleNamespace())

    await handler({"channel": channel, "temp": {}})

    assert sent == [{"type": "websocket.accept", "subprotocol": "jsonrpc"}]
    assert channel.state["transport_sent"] is True
