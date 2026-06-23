from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import Blueprint, Flask, jsonify


def build_health_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    return app


def build_router_app() -> Flask:
    app = Flask(__name__)
    blueprint = Blueprint("items", __name__, url_prefix="/v1")

    @blueprint.get("/items/<item_id>")
    def read_item(item_id: str):
        return jsonify({"id": item_id, "name": "Ada"})

    app.register_blueprint(blueprint)
    return app


@dataclass(frozen=True)
class ItemModel:
    id: str
    name: str


def build_table_projection() -> dict[str, Any]:
    return {
        "resource": "Item",
        "fields": {"id": "string", "name": "string"},
        "operations": ("create", "list", "read"),
        "profile": "resource",
        "bindings": ("http.rest", "http.jsonrpc"),
    }


def build_websocket_projection() -> dict[str, Any]:
    return {
        "path": "/ws/echo",
        "exchange": "bidirectional_stream",
        "framing": "json",
        "subprotocols": ("json",),
        "message": {"echo": "same text payload"},
    }


def build_sql_projection() -> dict[str, Any]:
    return {
        "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
        "lowerings": {
            "sqlite": {"id": "TEXT", "metadata": "JSON"},
            "postgres": {"id": "UUID", "metadata": "JSONB"},
        },
    }
