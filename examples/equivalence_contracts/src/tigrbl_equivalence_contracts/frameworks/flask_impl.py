from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from flask import Blueprint, Flask, jsonify


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


table_contract: dict[str, Any] = {
    "resource": "Item",
    "fields": {"id": "string", "name": "string"},
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


sql_contract = {
    "logical_fields": {"id": "uuid", "name": "string", "metadata": "json"},
    "lowerings": {
        "sqlite": {"id": "TEXT", "metadata": "JSON"},
        "postgres": {"id": "UUID", "metadata": "JSONB"},
    },
}
