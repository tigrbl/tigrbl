"""FastAPI implementation for the RestJsonRpcOlapTable Widget route surface."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_rest_json_rpc_olap_table"
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


@app.get("/widgetrestjsonrpcolaptable", response_model=list[WidgetOut])
def list_widgets() -> list[WidgetOut]:
    with Session(engine) as session:
        rows = session.query(WidgetRow).order_by(WidgetRow.id).all()
        return [WidgetOut(id=row.id, name=row.name) for row in rows]


@app.post("/widgetrestjsonrpcolaptable", response_model=WidgetOut, status_code=201)
def create_widget(payload: WidgetIn) -> WidgetOut:
    with Session(engine) as session:
        row = WidgetRow(id=payload.id, name=payload.name)
        session.add(row)
        session.commit()
        return WidgetOut(id=row.id, name=row.name)


@app.get("/widgetrestjsonrpcolaptable/{item_id}", response_model=WidgetOut)
def read_widget(item_id: str) -> WidgetOut:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise HTTPException(status_code=404)
        return WidgetOut(id=row.id, name=row.name)


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetRestJsonRpcOlapTable.count":
        return _rpc_count_widgets()
    if method == "WidgetRestJsonRpcOlapTable.exists":
        return _rpc_exists_widget(params["id"])
    if method == "WidgetRestJsonRpcOlapTable.list":
        return _rpc_list_widgets()
    if method == "WidgetRestJsonRpcOlapTable.aggregate":
        return {"field": params["field"], "op": "sum", "value": 0, "count": 0}
    if method == "WidgetRestJsonRpcOlapTable.group_by":
        return {"field": params["field"], "agg": "count", "groups": []}
    raise KeyError(method)


def _rpc_count_widgets() -> dict[str, int]:
    with Session(engine) as session:
        return {"count": int(session.scalar(select(func.count()).select_from(WidgetRow)))}


def _rpc_exists_widget(item_id: str) -> dict[str, bool]:
    with Session(engine) as session:
        return {"exists": session.get(WidgetRow, item_id) is not None}


def _rpc_list_widgets() -> list[dict[str, str]]:
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return [{"id": row.id, "name": row.name} for row in rows]
