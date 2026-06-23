from __future__ import annotations

from flask import Flask, abort, jsonify, request
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets"

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


@app.post("/widget")
def create_widget():
    payload = request.get_json()
    with Session(engine) as session:
        row = WidgetRow(id=payload["id"], name=payload["name"])
        session.add(row)
        session.commit()
        return jsonify({"id": row.id, "name": row.name}), 201


@app.get("/widget")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])


@app.get("/widget/<id>")
def read_widget(id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        return jsonify({"id": row.id, "name": row.name})


@app.patch("/widget/<id>")
def update_widget(id: str):
    payload = request.get_json()
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        row.name = payload["name"]
        session.commit()
        return jsonify({"id": row.id, "name": row.name})


@app.delete("/widget/<id>")
def delete_widget(id: str):
    with Session(engine) as session:
        row = session.get(WidgetRow, id)
        if row is None:
            abort(404)
        session.delete(row)
        session.commit()
        return jsonify({"deleted": 1})
