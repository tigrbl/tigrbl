"""Tigrbl implementation for the RestJsonRpcOltpTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestJsonRpcOltpTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestJsonRpcOltpTable(RestJsonRpcOltpTable):
    """A Widget resource authored with Tigrbl RestJsonRpcOltpTable."""

    __tablename__ = "widgets_rest_json_rpc_oltp_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestJsonRpcOltpTable)
app.initialize()
app.mount_jsonrpc(prefix="/rpc")
