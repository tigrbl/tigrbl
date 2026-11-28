"""FastAPI implementation for the JsonRpcOlapTable Widget JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_olap_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)
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


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetJsonRpcOlapTable.count":
        return _count_widgets()
    if method == "WidgetJsonRpcOlapTable.exists":
        return _exists_widget(params["id"])
    if method == "WidgetJsonRpcOlapTable.list":
        return _list_widgets()
    if method == "WidgetJsonRpcOlapTable.aggregate":
        return {"field": params["field"], "op": "sum", "value": 0, "count": 0}
    if method == "WidgetJsonRpcOlapTable.group_by":
        return {"field": params["field"], "agg": "count", "groups": []}
    raise KeyError(method)


def _count_widgets() -> dict[str, int]:
    with Session(engine) as session:
        return {"count": int(session.scalar(select(func.count()).select_from(WidgetRow)))}


def _exists_widget(item_id: str) -> dict[str, bool]:
    with Session(engine) as session:
        return {"exists": session.get(WidgetRow, item_id) is not None}


def _list_widgets() -> list[dict[str, str]]:
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return [{"id": row.id, "name": row.name} for row in rows]
