"""Flask implementation for the RestJsonRpcTable Widget route surface."""

from __future__ import annotations

from typing import Any

from flask import Flask, abort, jsonify, request
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from .runtime import ROUTES


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_rest_json_rpc_table"
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


@app.get("/widgetrestjsonrpctable")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.post("/widgetrestjsonrpctable")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.delete("/widgetrestjsonrpctable")
def clear_widgets():
    with Session(engine) as session:
        deleted = session.query(WidgetRow).delete()
        session.commit()
        return jsonify({"deleted": deleted})


@app.get("/widgetrestjsonrpctable/<item_id>")
def read_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


@app.patch("/widgetrestjsonrpctable/<item_id>")
def update_widget(item_id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.put("/widgetrestjsonrpctable/<item_id>")
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


@app.delete("/widgetrestjsonrpctable/<item_id>")
def delete_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        session.delete(row)
        session.commit()
        return jsonify({"deleted": 1})


def _dispatch_jsonrpc(method: str, params: dict[str, Any]) -> Any:
    if method == "WidgetRestJsonRpcTable.create":
        return _rpc_create_widget(params)
    if method == "WidgetRestJsonRpcTable.read":
        return _rpc_read_widget(params["id"])
    if method == "WidgetRestJsonRpcTable.list":
        return _rpc_list_widgets()
    if method == "WidgetRestJsonRpcTable.delete":
        return _rpc_delete_widget(params["id"])
    raise KeyError(method)


def _rpc_create_widget(payload: dict[str, str]) -> dict[str, str]:
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return {"id": row.id, "name": row.name}


def _rpc_read_widget(item_id: str) -> dict[str, str]:
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            raise KeyError(item_id)
        return {"id": row.id, "name": row.name}


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
