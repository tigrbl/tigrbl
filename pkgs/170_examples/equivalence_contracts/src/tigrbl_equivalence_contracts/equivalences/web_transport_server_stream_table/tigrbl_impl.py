"""Tigrbl implementation for the WebTransportServerStreamTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebTransportServerStreamTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebTransportServerStreamTable(WebTransportServerStreamTable):
    """A Widget resource authored with Tigrbl WebTransportServerStreamTable."""

    __tablename__ = "widgets_web_transport_server_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebTransportServerStreamTable)
app.initialize()
