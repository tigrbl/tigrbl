"""Tigrbl implementation for the RestJsonRpcOlapTable table-class equivalence."""

from __future__ import annotations

from tigrbl import RestJsonRpcOlapTable, TigrblApp
from tigrbl.types import Column, String


class WidgetRestJsonRpcOlapTable(RestJsonRpcOlapTable):
    """A Widget resource authored with Tigrbl RestJsonRpcOlapTable."""

    __tablename__ = "widgets_rest_json_rpc_olap_table"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)


app = TigrblApp(engine={"kind": "sqlite", "mode": "memory", "async": False})
app.include_table(WidgetRestJsonRpcOlapTable)
app.initialize()
