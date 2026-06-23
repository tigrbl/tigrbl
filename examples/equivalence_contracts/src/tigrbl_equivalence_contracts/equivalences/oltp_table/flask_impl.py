"""Flask route-surface implementation for Tigrbl OltpTable."""

from __future__ import annotations

from flask import Flask, jsonify

from .runtime import ROUTES

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


@app.get("/widgetoltptable")
def get_1():
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable", "method": "GET"})


@app.post("/widgetoltptable")
def post_2():
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable", "method": "POST"})


@app.get("/widgetoltptable/<item_id>")
def get_3(item_id: str):
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetoltptable/<item_id>")
def patch_4(item_id: str):
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetoltptable/<item_id>")
def put_5(item_id: str):
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetoltptable/<item_id>")
def delete_6(item_id: str):
    return jsonify({"table_class": "OltpTable", "path": "/widgetoltptable/{item_id}", "method": "DELETE", "item_id": item_id})
