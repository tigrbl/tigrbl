"""Tigrbl implementation for the WebTransportBidiTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebTransportBidiTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebTransportBidiTable(WebTransportBidiTable):
    """A Widget resource authored with Tigrbl WebTransportBidiTable."""

    __tablename__ = "widgets_web_transport_bidi_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebTransportBidiTable)
app.initialize()
