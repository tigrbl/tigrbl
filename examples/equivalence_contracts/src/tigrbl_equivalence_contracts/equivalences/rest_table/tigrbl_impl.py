"""Tigrbl implementation for the RestTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestTable(RestTable):
    """A Widget resource authored with Tigrbl RestTable."""

    __tablename__ = "widgets_rest_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestTable)
app.initialize()
