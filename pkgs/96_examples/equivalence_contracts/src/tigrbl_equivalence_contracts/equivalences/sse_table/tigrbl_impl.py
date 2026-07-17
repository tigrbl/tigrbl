"""Tigrbl implementation for the SseTable table-class equivalence."""

from __future__ import annotations

from tigrbl import SseTable, TigrblApp
from tigrbl.types import Column, String


class WidgetSseTable(SseTable):
    """A Widget resource authored with Tigrbl SseTable."""

    __tablename__ = "widgets_sse_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetSseTable)
app.initialize()
