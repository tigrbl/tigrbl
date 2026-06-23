"""Flask route-surface implementation for Tigrbl RestJsonRpcOlapTable."""

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


@app.get("/widgetrestjsonrpcolaptable")
def get_1():
    return jsonify({"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable", "method": "GET"})


@app.post("/widgetrestjsonrpcolaptable")
def post_2():
    return jsonify({"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable", "method": "POST"})


@app.get("/widgetrestjsonrpcolaptable/<item_id>")
def get_3(item_id: str):
    return jsonify({"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable/{item_id}", "method": "GET", "item_id": item_id})
