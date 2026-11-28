"""Runtime proof for the WebSocketTable table-class WebSocket surface."""

from __future__ import annotations

import asyncio
from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

WS_PATH = "/widgetwebsockettable"
EXPECTED_WEBSOCKET_EVIDENCE = (
    {
        "step": "message_exchange",
        "path": WS_PATH,
        "sent": "ping",
        "received": "widget:ping",
    },
)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert a real WebSocket message exchange."""

    server = start_http_server(app, server_kind)
    try:
        evidence = asyncio.run(_assert_websocket_exchange(server.base_url))
    finally:
        server.stop()
    assert evidence == EXPECTED_WEBSOCKET_EVIDENCE
    return evidence


async def _assert_websocket_exchange(base_url: str) -> tuple[dict[str, Any], ...]:
    import websockets

    ws_url = base_url.replace("http://", "ws://", 1) + WS_PATH
    async with websockets.connect(ws_url) as websocket:
        await websocket.send("ping")
        received = await websocket.recv()
    return (
        {
            "step": "message_exchange",
            "path": WS_PATH,
            "sent": "ping",
            "received": received,
        },
    )
