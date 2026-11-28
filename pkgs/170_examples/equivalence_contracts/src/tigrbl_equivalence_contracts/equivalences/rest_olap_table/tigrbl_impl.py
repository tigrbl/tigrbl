"""Tigrbl implementation for the RestOlapTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestOlapTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestOlapTable(RestOlapTable):
    """A Widget resource authored with Tigrbl RestOlapTable."""

    __tablename__ = "widgets_rest_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestOlapTable)
app.initialize()
