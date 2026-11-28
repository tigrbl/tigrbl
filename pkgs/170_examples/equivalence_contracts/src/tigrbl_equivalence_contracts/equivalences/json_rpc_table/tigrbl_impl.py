"""Tigrbl implementation for the JsonRpcTable table-class equivalence."""

from __future__ import annotations

from tigrbl import JsonRpcTable, TigrblApp
from tigrbl.types import Column, String


class WidgetJsonRpcTable(JsonRpcTable):
    """A Widget resource authored with Tigrbl JsonRpcTable."""

    __tablename__ = "widgets_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetJsonRpcTable)
app.initialize()
