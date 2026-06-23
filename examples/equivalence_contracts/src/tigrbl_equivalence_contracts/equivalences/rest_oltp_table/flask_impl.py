"""Flask route-surface implementation for Tigrbl RestOltpTable."""

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


@app.get("/widgetrestoltptable")
def get_1():
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable", "method": "GET"})


@app.post("/widgetrestoltptable")
def post_2():
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable", "method": "POST"})


@app.get("/widgetrestoltptable/<item_id>")
def get_3(item_id: str):
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetrestoltptable/<item_id>")
def patch_4(item_id: str):
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetrestoltptable/<item_id>")
def put_5(item_id: str):
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetrestoltptable/<item_id>")
def delete_6(item_id: str):
    return jsonify({"table_class": "RestOltpTable", "path": "/widgetrestoltptable/{item_id}", "method": "DELETE", "item_id": item_id})
