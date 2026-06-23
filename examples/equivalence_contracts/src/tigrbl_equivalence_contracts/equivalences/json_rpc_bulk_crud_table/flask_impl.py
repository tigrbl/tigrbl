"""Flask implementation for the JsonRpcBulkCrudTable Widget route surface."""

from __future__ import annotations

from flask import Flask, abort, jsonify, request
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from .runtime import ROUTES


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_json_rpc_bulk_crud_table"
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


@app.get("/widgetjsonrpcbulkcrudtable")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.post("/widgetjsonrpcbulkcrudtable")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.patch("/widgetjsonrpcbulkcrudtable")
def bulk_update_widgets():
    payload = request.get_json()
    with Session(engine) as session:
        output = []
        for item in payload:
            row = session.get(WidgetRow, item["id"])
            if row is None:
                continue
            row.name = item["name"]
            output.append({"id": row.id, "name": row.name})
        session.commit()
        return jsonify(output)


@app.put("/widgetjsonrpcbulkcrudtable")
def bulk_replace_widgets():
    payload = request.get_json()
    with Session(engine) as session:
        output = []
        for item in payload:
            row = session.get(WidgetRow, item["id"])
            if row is None:
                row = WidgetRow(id=item["id"], name=item["name"])
                session.add(row)
            else:
                row.name = item["name"]
            output.append({"id": row.id, "name": row.name})
        session.commit()
        return jsonify(output)


@app.delete("/widgetjsonrpcbulkcrudtable")
def clear_widgets():
    with Session(engine) as session:
        deleted = session.query(WidgetRow).delete()
        session.commit()
        return jsonify({"deleted": deleted})


@app.get("/widgetjsonrpcbulkcrudtable/<item_id>")
def read_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


@app.patch("/widgetjsonrpcbulkcrudtable/<item_id>")
def update_widget(item_id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.put("/widgetjsonrpcbulkcrudtable/<item_id>")
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


@app.delete("/widgetjsonrpcbulkcrudtable/<item_id>")
def delete_widget(item_id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, item_id)
        if row is None:
            abort(404)
        session.delete(row)
        session.commit()
        return jsonify({"deleted": 1})
