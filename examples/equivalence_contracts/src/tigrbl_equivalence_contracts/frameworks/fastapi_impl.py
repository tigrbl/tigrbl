from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, WebSocket
from pydantic import BaseModel


health_app = FastAPI()


@health_app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


router_app = FastAPI()
router = APIRouter(prefix="/v1")


@router.get("/items/{item_id}")
def read_item(item_id: str) -> dict[str, str]:
    return {"id": item_id, "name": "Ada"}


router_app.include_router(router)


class ItemModel(BaseModel):
    id: str
    name: str


table_contract: dict[str, Any] = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string"},
    "operations": ("create", "list", "read"),
    "profile": "resource",
    "bindings": ("http.rest", "http.jsonrpc"),
}


websocket_app = FastAPI()


@websocket_app.websocket("/ws/echo")
async def echo(websocket: WebSocket) -> None:
    await websocket.accept(subprotocol="json")
    await websocket.send_text(await websocket.receive_text())


websocket_contract = {
    "path": "/ws/echo",
    "exchange": "bidirectional_stream",
    "framing": "json",
    "subprotocols": ("json",),
    "message": {"echo": "same text payload"},
}


sql_contract = {
    "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
    "lowerings": {
        "sqlite": {"id": "TEXT", "metadata": "JSON"},
        "postgres": {"id": "UUID", "metadata": "JSONB"},
    },
}
