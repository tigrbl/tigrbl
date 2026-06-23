"""Flask route-surface implementation for Tigrbl RestBulkCrudTable."""

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


@app.get("/widgetrestbulkcrudtable")
def get_1():
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable", "method": "GET"})


@app.post("/widgetrestbulkcrudtable")
def post_2():
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable", "method": "POST"})


@app.patch("/widgetrestbulkcrudtable")
def patch_3():
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable", "method": "PATCH"})


@app.put("/widgetrestbulkcrudtable")
def put_4():
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable", "method": "PUT"})


@app.delete("/widgetrestbulkcrudtable")
def delete_5():
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable", "method": "DELETE"})


@app.get("/widgetrestbulkcrudtable/<item_id>")
def get_6(item_id: str):
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetrestbulkcrudtable/<item_id>")
def patch_7(item_id: str):
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetrestbulkcrudtable/<item_id>")
def put_8(item_id: str):
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetrestbulkcrudtable/<item_id>")
def delete_9(item_id: str):
    return jsonify({"table_class": "RestBulkCrudTable", "path": "/widgetrestbulkcrudtable/{item_id}", "method": "DELETE", "item_id": item_id})
