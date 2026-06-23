from __future__ import annotations

from typing import Any

from tigrbl import (
    TableBase,
    TigrblApp,
    TigrblRouter,
    WebSocketBindingSpec,
)
from tigrbl.factories.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String
from tigrbl_core._spec.datatypes import DataTypeSpec, EngineDatatypeBridge
from tigrbl_core._spec.table_profile_spec import get_builtin_table_profile_definition


ITEM = {"id": "item-1", "name": "Ada"}


def build_health_app() -> TigrblApp:
    app = TigrblApp()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def build_router_app() -> TigrblApp:
    app = TigrblApp()
    router = TigrblRouter(prefix="/v1")

    @router.get("/items/{item_id}")
    def read_item(item_id: str) -> dict[str, str]:
        return {"id": item_id, "name": "Ada"}

    app.include_router(router)
    return app


class ItemTable(TableBase, GUIDPk):
    __tablename__ = "equivalence_item"
    __allow_unmapped__ = True

    name = Column(String, nullable=False)


def build_table_projection() -> dict[str, Any]:
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(ItemTable)
    app.initialize()
    profile = get_builtin_table_profile_definition("rest_jsonrpc")
    return {
        "resource": "Item",
        "fields": {"id": "string", "name": "string"},
        "operations": ("create", "list", "read"),
        "profile": "resource",
        "bindings": tuple(kind for kind in profile.binding_families if kind in {"http.rest", "http.jsonrpc"}),
    }


def build_websocket_projection() -> dict[str, Any]:
    app = TigrblApp()

    @app.websocket("/ws/echo", framing="json", subprotocols=("json",))
    async def echo(websocket: Any) -> None:
        await websocket.accept()
        await websocket.send_text(await websocket.receive_text())

    binding = WebSocketBindingSpec(
        proto="ws",
        path="/ws/echo",
        framing="json",
        subprotocols=("json",),
    )
    return {
        "path": binding.path,
        "exchange": binding.exchange,
        "framing": binding.framing,
        "subprotocols": binding.subprotocols,
        "message": {"echo": "same text payload"},
    }


def build_sql_projection() -> dict[str, Any]:
    bridge = EngineDatatypeBridge()
    return {
        "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
        "lowerings": {
            "sqlite": {
                "id": bridge.lower("sqlite", DataTypeSpec("uuid"), strict=True).physical_name,
                "metadata": bridge.lower("sqlite", DataTypeSpec("json"), strict=True).physical_name,
            },
            "postgres": {
                "id": bridge.lower("postgres", DataTypeSpec("uuid"), strict=True).physical_name,
                "metadata": bridge.lower("postgres", DataTypeSpec("json"), strict=True).physical_name,
            },
        },
    }
