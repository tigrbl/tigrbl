"""Runtime proof for the WebSocketJsonRpcTable WebSocket JSON-RPC surface."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from tigrbl_equivalence_contracts.runtime import ServerKind, start_http_server

WS_PATH = "/widgetwebsocketjsonrpctable"
EXPECTED_WEBSOCKET_JSONRPC_EVIDENCE = (
    {
        "step": "jsonrpc_message_exchange",
        "path": WS_PATH,
        "subprotocol": "jsonrpc",
        "sent_method": "WidgetWebSocketJsonRpcTable.echo",
        "envelope": {
            "jsonrpc": "2.0",
            "id": 1,
            "result": {"message": "widget:ping"},
        },
    },
)


def assert_equivalence(app: Any, server_kind: ServerKind) -> tuple[dict[str, Any], ...]:
    """Start one vendor app and assert WebSocket JSON-RPC framing."""

    server = start_http_server(app, server_kind)
    try:
        evidence = asyncio.run(_assert_websocket_jsonrpc_exchange(server.base_url))
    finally:
        server.stop()
    assert evidence == EXPECTED_WEBSOCKET_JSONRPC_EVIDENCE
    return evidence


async def _assert_websocket_jsonrpc_exchange(
    base_url: str,
) -> tuple[dict[str, Any], ...]:
    import websockets

    ws_url = base_url.replace("http://", "ws://", 1) + WS_PATH
    request = {
        "jsonrpc": "2.0",
        "method": "WidgetWebSocketJsonRpcTable.echo",
        "params": {"message": "ping"},
        "id": 1,
    }
    async with websockets.connect(ws_url, subprotocols=["jsonrpc"]) as websocket:
        assert websocket.subprotocol == "jsonrpc"
        await websocket.send(json.dumps(request))
        response = await websocket.recv()
    envelope = json.loads(response)
    assert envelope["jsonrpc"] == "2.0"
    assert envelope["id"] == request["id"]
    assert envelope["result"] == {"message": "widget:ping"}
    return (
        {
            "step": "jsonrpc_message_exchange",
            "path": WS_PATH,
            "subprotocol": "jsonrpc",
            "sent_method": request["method"],
            "envelope": envelope,
        },
    )
