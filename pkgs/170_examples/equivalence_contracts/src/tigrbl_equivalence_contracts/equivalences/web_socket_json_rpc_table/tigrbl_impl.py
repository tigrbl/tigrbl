"""Tigrbl implementation for the WebSocketJsonRpcTable table-class equivalence."""

from __future__ import annotations

import json

from tigrbl import WebSocketJsonRpcTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebSocketJsonRpcTable(WebSocketJsonRpcTable):
    """A Widget resource authored with Tigrbl WebSocketJsonRpcTable."""

    __tablename__ = "widgets_web_socket_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebSocketJsonRpcTable)
app.initialize()


@app.websocket(
    "/widgetwebsocketjsonrpctable",
    framing="jsonrpc",
    subprotocols=("jsonrpc",),
)
async def widget_socket_jsonrpc(websocket):
    """Handle one JSON-RPC envelope over Tigrbl's WebSocket runtime surface."""

    await websocket.accept(subprotocol="jsonrpc")
    envelope = json.loads(await websocket.receive_text())
    result = {"message": f"widget:{envelope['params']['message']}"}
    await websocket.send_text(
        json.dumps(
            {
                "jsonrpc": "2.0",
                "id": envelope["id"],
                "result": result,
            },
            separators=(",", ":"),
        )
    )
    await websocket.close()
