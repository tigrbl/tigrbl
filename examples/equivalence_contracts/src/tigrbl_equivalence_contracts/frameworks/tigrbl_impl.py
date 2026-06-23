from __future__ import annotations

from typing import Any

from tigrbl import (
    TableBase,
    TigrblApp,
    TigrblRouter,
    WebSocketBindingSpec,
)
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_core._spec.datatypes import DataTypeSpec, EngineDatatypeBridge
from tigrbl_core._spec.table_profile_spec import get_builtin_table_profile_definition


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


class ItemTable(TableBase, GUIDPk):
    __tablename__ = "equivalence_item"
    __allow_unmapped__ = True

    name = Column(String, nullable=False)


table_app = TigrblApp()
table_app.include_table(ItemTable)
table_app.initialize()

table_profile = get_builtin_table_profile_definition("rest_jsonrpc")
table_contract = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string"},
    "operations": ("create", "list", "read"),
    "profile": "resource",
    "bindings": tuple(
        kind
        for kind in table_profile.binding_families
        if kind in {"http.rest", "http.jsonrpc"}
    ),
}


websocket_app = TigrblApp()


@websocket_app.websocket("/ws/echo", framing="json", subprotocols=("json",))
async def echo(websocket: Any) -> None:
    await websocket.accept()
    await websocket.send_text(await websocket.receive_text())


websocket_binding = WebSocketBindingSpec(
    proto="ws",
    path="/ws/echo",
    framing="json",
    subprotocols=("json",),
)
websocket_contract = {
    "path": websocket_binding.path,
    "exchange": websocket_binding.exchange,
    "framing": websocket_binding.framing,
    "subprotocols": websocket_binding.subprotocols,
    "message": {"echo": "same text payload"},
}


datatype_bridge = EngineDatatypeBridge()
sql_contract = {
    "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
    "lowerings": {
        "sqlite": {
            "id": datatype_bridge.lower(
                "sqlite", DataTypeSpec("uuid"), strict=True
            ).physical_name,
            "metadata": datatype_bridge.lower(
                "sqlite", DataTypeSpec("json"), strict=True
            ).physical_name,
        },
        "postgres": {
            "id": datatype_bridge.lower(
                "postgres", DataTypeSpec("uuid"), strict=True
            ).physical_name,
            "metadata": datatype_bridge.lower(
                "postgres", DataTypeSpec("json"), strict=True
            ).physical_name,
        },
    },
}
