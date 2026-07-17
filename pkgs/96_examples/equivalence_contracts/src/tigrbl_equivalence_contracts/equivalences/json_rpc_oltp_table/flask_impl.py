"""Flask implementation for the JsonRpcOltpTable Widget JSON-RPC surface."""

from __future__ import annotations

from typing import Any

from flask import Flask, jsonify, request
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_oltp_table"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


engine = create_engine(
    "sqlite+pysqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    future=True,
)
Base.metadata.create_all(engine)
app = Flask(__name__)


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.post("/rpc")
def jsonrpc():
    envelope = request.get_json()
    method = envelope.get("method")
    params = envelope.get("params") or {}
    request_id = envelope.get("id")
    try:
        result = _dispatch_jsonrpc(method, params)
        return jsonify({"jsonrpc": "2.0", "result": result, "id": request_id})
    except KeyError as exc:
        return jsonify(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"unknown method: {exc.args[0]}"},
                "id": request_id,
            }
        )


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetJsonRpcOltpTable.create":
        return _create_widget(params)
    if method == "WidgetJsonRpcOltpTable.count":
        return _count_widgets()
    if method == "WidgetJsonRpcOltpTable.exists":
        return _exists_widget(params["id"])
    if method == "WidgetJsonRpcOltpTable.list":
        return _list_widgets()
    if method == "WidgetJsonRpcOltpTable.delete":
        return _delete_widget(params["id"])
    raise KeyError(method)


def _create_widget(payload: dict[str, str]) -> dict[str, str]:
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return {"id": row.id, "name": row.name}


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


def _delete_widget(item_id: str) -> dict[str, int]:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise KeyError(item_id)
        session.delete(row)
        session.commit()
        return {"deleted": 1}
