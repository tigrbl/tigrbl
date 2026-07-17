"""Tigrbl implementation for the JsonRpcOlapTable table-class equivalence."""

from __future__ import annotations

from tigrbl import JsonRpcOlapTable, TigrblApp
from tigrbl.types import Column, String


class WidgetJsonRpcOlapTable(JsonRpcOlapTable):
    """A Widget resource authored with Tigrbl JsonRpcOlapTable."""

    __tablename__ = "widgets_json_rpc_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetJsonRpcOlapTable)
app.initialize()
app.mount_jsonrpc(prefix="/rpc")
