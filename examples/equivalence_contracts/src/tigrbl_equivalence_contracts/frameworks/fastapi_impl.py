from __future__ import annotations

from typing import Any

from fastapi import APIRouter, FastAPI, WebSocket
from pydantic import BaseModel
from sqlalchemy import JSON, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    metadata: dict[str, Any]


class Base(DeclarativeBase):
    pass


class ItemRow(Base):
    __tablename__ = "equivalence_item"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False
    )


table_contract: dict[str, Any] = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string", "metadata": "json"},
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


sqlite_dialect = sqlite.dialect()
sql_contract = {
    "dialect": "sqlite",
    "table": ItemRow.__tablename__,
    "columns": tuple(
        (column.name, column.type.compile(dialect=sqlite_dialect), column.primary_key)
        for column in ItemRow.__table__.columns
    ),
}
