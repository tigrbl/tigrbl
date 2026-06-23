"""Tigrbl implementation for the JsonRpcBulkCrudTable table-class equivalence."""

from __future__ import annotations

from tigrbl import JsonRpcBulkCrudTable, TigrblApp
from tigrbl.types import Column, String


class WidgetJsonRpcBulkCrudTable(JsonRpcBulkCrudTable):
    """A Widget resource authored with Tigrbl JsonRpcBulkCrudTable."""

    __tablename__ = "widgets_json_rpc_bulk_crud_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetJsonRpcBulkCrudTable)
app.initialize()
