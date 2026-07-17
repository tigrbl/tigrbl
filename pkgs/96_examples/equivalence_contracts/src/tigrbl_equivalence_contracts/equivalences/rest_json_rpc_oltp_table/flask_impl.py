"""Flask implementation for the RestJsonRpcOltpTable Widget route surface."""

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
    __tablename__ = "widgets_rest_json_rpc_oltp_table"
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


@app.get("/widgetrestjsonrpcoltptable")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.post("/widgetrestjsonrpcoltptable")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.get("/widgetrestjsonrpcoltptable/<item_id>")
def read_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


@app.patch("/widgetrestjsonrpcoltptable/<item_id>")
def update_widget(item_id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.put("/widgetrestjsonrpcoltptable/<item_id>")
def replace_widget(item_id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            row = WidgetRow(id=item_id, name=payload["name"])
            session.add(row)
        else:
            row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.delete("/widgetrestjsonrpcoltptable/<item_id>")
def delete_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        session.delete(row)
        session.commit()
        return jsonify({"deleted": 1})


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetRestJsonRpcOltpTable.create":
        return _rpc_create_widget(params)
    if method == "WidgetRestJsonRpcOltpTable.count":
        return _rpc_count_widgets()
    if method == "WidgetRestJsonRpcOltpTable.exists":
        return _rpc_exists_widget(params["id"])
    if method == "WidgetRestJsonRpcOltpTable.list":
        return _rpc_list_widgets()
    if method == "WidgetRestJsonRpcOltpTable.delete":
        return _rpc_delete_widget(params["id"])
    raise KeyError(method)


def _rpc_create_widget(payload: dict[str, str]) -> dict[str, str]:
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return {"id": row.id, "name": row.name}


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


def _rpc_delete_widget(item_id: str) -> dict[str, int]:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise KeyError(item_id)
        session.delete(row)
        session.commit()
        return {"deleted": 1}
