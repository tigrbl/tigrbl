from __future__ import annotations

from typing import Any

from tigrbl import (
    RestJsonRpcTable,
    TigrblApp,
    TigrblRouter,
    TableSpec,
    websocket_ctx,
)
from tigrbl.types import Column, JSON, String
from sqlalchemy.dialects import sqlite


health_app = TigrblApp()


@health_app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


router_app = TigrblApp()
router = TigrblRouter(prefix="/v1")


@router.get("/items/{item_id}")
def read_item(item_id: str) -> dict[str, str]:
    return {"id": item_id, "name": "Ada"}


router_app.include_router(router)


class ItemTable(RestJsonRpcTable):
    __tablename__ = "equivalence_item"
    __allow_unmapped__ = True

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    meta = Column("metadata", JSON, nullable=False)


table_app = TigrblApp()
table_app.include_table(ItemTable)
table_app.initialize()

item_table_spec = TableSpec.collect(ItemTable)
table_contract = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string", "metadata": "json"},
    "operations": ("create", "list", "read"),
    "profile": "resource",
    "bindings": tuple(
        family
        for family, binding_type in (
            ("http.rest", "HttpRestBindingSpec"),
            ("http.jsonrpc", "HttpJsonRpcBindingSpec"),
        )
        if any(
            type(binding).__name__ == binding_type
            for op in item_table_spec.ops
            for binding in tuple(op.bindings or ())
        )
    ),
}


websocket_app = TigrblApp()


@websocket_ctx(
    "/ws/echo",
    alias="echo",
    framing="json",
    subprotocols=("json",),
    bind=websocket_app,
)
def echo(cls, ctx: dict[str, Any]) -> dict[str, str]:
    return {"echo": str(ctx.get("text", ""))}


websocket_spec = echo.__func__.__tigrbl_op_spec__
websocket_binding = websocket_spec.bindings[0]
websocket_contract = {
    "path": websocket_binding.path,
    "exchange": websocket_binding.exchange,
    "framing": websocket_binding.framing,
    "subprotocols": websocket_binding.subprotocols,
    "message": {"echo": "same text payload"},
}


sqlite_dialect = sqlite.dialect()
sql_contract = {
    "dialect": "sqlite",
    "table": ItemTable.__tablename__,
    "columns": tuple(
        (column.name, column.type.compile(dialect=sqlite_dialect), column.primary_key)
        for column in ItemTable.__table__.columns
    ),
}
