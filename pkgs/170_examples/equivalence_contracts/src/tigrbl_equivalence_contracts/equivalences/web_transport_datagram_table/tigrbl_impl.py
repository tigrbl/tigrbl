"""Tigrbl implementation for the WebTransportDatagramTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebTransportDatagramTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebTransportDatagramTable(WebTransportDatagramTable):
    """A Widget resource authored with Tigrbl WebTransportDatagramTable."""

    __tablename__ = "widgets_web_transport_datagram_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebTransportDatagramTable)
app.initialize()
