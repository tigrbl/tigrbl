"""Tigrbl implementation for the RestOltpTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestOltpTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestOltpTable(RestOltpTable):
    """A Widget resource authored with Tigrbl RestOltpTable."""

    __tablename__ = "widgets_rest_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestOltpTable)
app.initialize()
