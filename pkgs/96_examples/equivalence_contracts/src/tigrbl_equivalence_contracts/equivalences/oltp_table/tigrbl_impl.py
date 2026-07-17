"""Tigrbl implementation for the OltpTable table-class equivalence."""

from __future__ import annotations

from tigrbl import OltpTable, TigrblApp
from tigrbl.types import Column, String


class WidgetOltpTable(OltpTable):
    """A Widget resource authored with Tigrbl OltpTable."""

    __tablename__ = "widgets_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetOltpTable)
app.initialize()
