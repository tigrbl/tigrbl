"""Tigrbl implementation for the EventStreamTable table-class equivalence."""

from __future__ import annotations

from tigrbl import EventStreamTable, TigrblApp
from tigrbl.types import Column, String


class WidgetEventStreamTable(EventStreamTable):
    """A Widget resource authored with Tigrbl EventStreamTable."""

    __tablename__ = "widgets_event_stream_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetEventStreamTable)
app.initialize()
