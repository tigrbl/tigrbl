"""Flask route-surface implementation for Tigrbl RestOlapTable."""

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


@app.get("/widgetrestolaptable")
def get_1():
    return jsonify({"table_class": "RestOlapTable", "path": "/widgetrestolaptable", "method": "GET"})


@app.post("/widgetrestolaptable")
def post_2():
    return jsonify({"table_class": "RestOlapTable", "path": "/widgetrestolaptable", "method": "POST"})


@app.get("/widgetrestolaptable/<item_id>")
def get_3(item_id: str):
    return jsonify({"table_class": "RestOlapTable", "path": "/widgetrestolaptable/{item_id}", "method": "GET", "item_id": item_id})
