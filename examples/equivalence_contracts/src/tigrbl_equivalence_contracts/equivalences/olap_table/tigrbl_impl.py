"""Tigrbl implementation for the OlapTable table-class equivalence."""

from __future__ import annotations

from tigrbl import OlapTable, TigrblApp
from tigrbl.types import Column, String


class WidgetOlapTable(OlapTable):
    """A Widget resource authored with Tigrbl OlapTable."""

    __tablename__ = "widgets_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetOlapTable)
app.initialize()
