"""Tigrbl implementation for the WebTransportTable table-class equivalence."""

from __future__ import annotations

from tigrbl import WebTransportTable, TigrblApp
from tigrbl.types import Column, String


class WidgetWebTransportTable(WebTransportTable):
    """A Widget resource authored with Tigrbl WebTransportTable."""

    __tablename__ = "widgets_web_transport_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetWebTransportTable)
app.initialize()
