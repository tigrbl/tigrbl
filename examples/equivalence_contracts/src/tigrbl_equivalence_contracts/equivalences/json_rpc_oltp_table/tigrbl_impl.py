"""Tigrbl implementation for the JsonRpcOltpTable table-class equivalence."""

from __future__ import annotations

from tigrbl import JsonRpcOltpTable, TigrblApp
from tigrbl.types import Column, String


class WidgetJsonRpcOltpTable(JsonRpcOltpTable):
    """A Widget resource authored with Tigrbl JsonRpcOltpTable."""

    __tablename__ = "widgets_json_rpc_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetJsonRpcOltpTable)
app.initialize()
