"""Flask implementation for the RestJsonRpcOlapTable Widget route surface."""

from __future__ import annotations

from typing import Any

from flask import Flask, abort, jsonify, request
from sqlalchemy import String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from .runtime import ROUTES


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


@app.get("/openapi.json")
def openapi_json():
    return jsonify(
        {
            "openapi": "3.1.0",
            "paths": {
                path: {method.lower(): {} for method in methods}
                for path, methods in ROUTES
            },
        }
    )


@app.get("/widgetrestjsonrpcolaptable")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.post("/widgetrestjsonrpcolaptable")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.get("/widgetrestjsonrpcolaptable/<item_id>")
def read_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


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
