"""Tigrbl implementation for the RestJsonRpcTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestJsonRpcTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestJsonRpcTable(RestJsonRpcTable):
    """A Widget resource authored with Tigrbl RestJsonRpcTable."""

    __tablename__ = "widgets_rest_json_rpc_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestJsonRpcTable)
app.initialize()
