"""Tigrbl implementation for the WebSocketJsonRpcTable table-class equivalence."""

from __future__ import annotations

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
