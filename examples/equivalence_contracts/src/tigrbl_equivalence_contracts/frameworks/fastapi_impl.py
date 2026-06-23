from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, WebSocket
from pydantic import BaseModel


def build_health_app() -> FastAPI:
    app = FastAPI()

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def build_router_app() -> FastAPI:
    app = FastAPI()
    router = APIRouter(prefix="/v1")

    @router.get("/items/{item_id}")
    def read_item(item_id: str) -> dict[str, str]:
        return {"id": item_id, "name": "Ada"}

    app.include_router(router)
    return app


class ItemModel(BaseModel):
    id: str
    name: str


def build_table_projection() -> dict[str, Any]:
    return {
        "resource": "Item",
        "fields": {"id": "string", "name": "string"},
        "operations": ("create", "list", "read"),
        "profile": "resource",
        "bindings": ("http.rest", "http.jsonrpc"),
    }


def build_websocket_projection() -> dict[str, Any]:
    app = FastAPI()

    @app.websocket("/ws/echo")
    async def echo(websocket: WebSocket) -> None:
        await websocket.accept(subprotocol="json")
        await websocket.send_text(await websocket.receive_text())

    return {
        "path": "/ws/echo",
        "exchange": "bidirectional_stream",
        "framing": "json",
        "subprotocols": ("json",),
        "message": {"echo": "same text payload"},
    }


def build_sql_projection() -> dict[str, Any]:
    return {
        "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
        "lowerings": {
            "sqlite": {"id": "TEXT", "metadata": "JSON"},
            "postgres": {"id": "UUID", "metadata": "JSONB"},
        },
    }
