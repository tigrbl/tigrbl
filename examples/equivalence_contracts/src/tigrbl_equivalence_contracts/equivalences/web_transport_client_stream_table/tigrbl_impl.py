"""Tigrbl implementation for the WebTransportClientStreamTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebTransportClientStreamTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebTransportClientStreamTable(WebTransportClientStreamTable):
    """A Widget resource authored with Tigrbl WebTransportClientStreamTable."""

    __tablename__ = "widgets_web_transport_client_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebTransportClientStreamTable)
app.initialize()
