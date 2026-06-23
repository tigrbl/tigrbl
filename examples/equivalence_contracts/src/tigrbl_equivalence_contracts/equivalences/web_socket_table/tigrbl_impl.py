"""Tigrbl implementation for the WebSocketTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebSocketTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebSocketTable(WebSocketTable):
    """A Widget resource authored with Tigrbl WebSocketTable."""

    __tablename__ = "widgets_web_socket_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebSocketTable)
app.initialize()
