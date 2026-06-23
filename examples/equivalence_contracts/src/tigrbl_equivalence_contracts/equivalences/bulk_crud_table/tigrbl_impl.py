"""Tigrbl implementation for the BulkCrudTable table-class equivalence."""

from __future__ import annotations

from tigrbl import BulkCrudTable, TigrblApp
from tigrbl.types import Column, String


class WidgetBulkCrudTable(BulkCrudTable):
    """A Widget resource authored with Tigrbl BulkCrudTable."""

    __tablename__ = "widgets_bulk_crud_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetBulkCrudTable)
app.initialize()
