"""Tigrbl implementation for the RestBulkCrudTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestBulkCrudTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestBulkCrudTable(RestBulkCrudTable):
    """A Widget resource authored with Tigrbl RestBulkCrudTable."""

    __tablename__ = "widgets_rest_bulk_crud_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestBulkCrudTable)
app.initialize()
