"""Flask implementation for the EventStreamTable Widget route surface."""

from __future__ import annotations

from flask import Flask, jsonify
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column
from sqlalchemy.pool import StaticPool

from .runtime import ROUTES


class Base(DeclarativeBase):
    pass


class WidgetRow(Base):
    __tablename__ = "widgets_event_stream_table"
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


@app.get("/widgeteventstreamtable")
def list_widgets():
    with Session(engine) as session:
        rows = session.scalars(select(WidgetRow).order_by(WidgetRow.id)).all()
        return jsonify([{"id": row.id, "name": row.name} for row in rows])
