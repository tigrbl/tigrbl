"""Tigrbl implementation for the StreamTable table-class equivalence."""

from __future__ import annotations

from tigrbl import StreamTable, TigrblApp
from tigrbl.types import Column, String


class WidgetStreamTable(StreamTable):
    """A Widget resource authored with Tigrbl StreamTable."""

    __tablename__ = "widgets_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetStreamTable)
app.initialize()
