from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import Blueprint, Flask, jsonify
from sqlalchemy import JSON, String
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


health_app = Flask(__name__)


@health_app.get("/health")
def health():
    return jsonify({"status": "ok"})


router_app = Flask(__name__)
blueprint = Blueprint("items", __name__, url_prefix="/v1")


@blueprint.get("/items/<item_id>")
def read_item(item_id: str):
    return jsonify({"id": item_id, "name": "Ada"})


router_app.register_blueprint(blueprint)


@dataclass(frozen=True)
class ItemModel:
    id: str
    name: str
    metadata: dict[str, Any]


class Base(DeclarativeBase):
    pass


class ItemRow(Base):
    __tablename__ = "equivalence_item"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    metadata_: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False
    )


table_contract: dict[str, Any] = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string", "metadata": "json"},
    "operations": ("create", "list", "read"),
    "profile": "resource",
    "bindings": ("http.rest", "http.jsonrpc"),
}


websocket_contract = {
    "path": "/ws/echo",
    "exchange": "bidirectional_stream",
    "framing": "json",
    "subprotocols": ("json",),
    "message": {"echo": "same text payload"},
}


sqlite_dialect = sqlite.dialect()
sql_contract = {
    "dialect": "sqlite",
    "table": ItemRow.__tablename__,
    "columns": tuple(
        (column.name, column.type.compile(dialect=sqlite_dialect), column.primary_key)
        for column in ItemRow.__table__.columns
    ),
}
