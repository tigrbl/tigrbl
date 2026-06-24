"""FastAPI implementation for the JsonRpcTable Widget JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)


class WidgetIn(BaseModel):
    id: str
    name: str


class WidgetOut(BaseModel):
    id: str
    name: str


app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/rpc")
async def jsonrpc(request: Request) -> dict[str, Any]:
    """Handle JSON-RPC 2.0 envelopes for the Widget table analogue."""

    envelope = await request.json()
    method = envelope.get("method")
    params = envelope.get("params") or {}
    request_id = envelope.get("id")
    try:
        result = _dispatch_jsonrpc(method, params)
        return {"jsonrpc": "2.0", "result": result, "id": request_id}
    except KeyError as exc:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": f"unknown method: {exc.args[0]}"},
            "id": request_id,
        }


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetJsonRpcTable.create":
        return _create_widget(params).model_dump()
    if method == "WidgetJsonRpcTable.read":
        return _read_widget(params["id"]).model_dump()
    if method == "WidgetJsonRpcTable.list":
        return [item.model_dump() for item in _list_widgets()]
    if method == "WidgetJsonRpcTable.delete":
        return _delete_widget(params["id"])
    raise KeyError(method)


def _list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return [WidgetOut(id=row.id, name=row.name) for row in rows]


def _create_widget(payload: dict[str, Any]) -> WidgetOut:
    item = WidgetIn(**payload)
    with Session(engine) as session:
        row = WidgetRow(id=item.id, name=item.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


def _read_widget(item_id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise KeyError(item_id)
        return WidgetOut(id=row.id, name=row.name)


def _delete_widget(item_id: str) -> dict[str, int]:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise KeyError(item_id)
        session.delete(row)
        session.commit()
        return {"deleted": 1}
