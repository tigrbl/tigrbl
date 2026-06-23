"""Flask route-surface implementation for Tigrbl JsonRpcTable."""

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


@app.get("/widgetjsonrpctable")
def get_1():
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable", "method": "GET"})


@app.post("/widgetjsonrpctable")
def post_2():
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable", "method": "POST"})


@app.delete("/widgetjsonrpctable")
def delete_3():
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable", "method": "DELETE"})


@app.get("/widgetjsonrpctable/<item_id>")
def get_4(item_id: str):
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetjsonrpctable/<item_id>")
def patch_5(item_id: str):
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetjsonrpctable/<item_id>")
def put_6(item_id: str):
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetjsonrpctable/<item_id>")
def delete_7(item_id: str):
    return jsonify({"table_class": "JsonRpcTable", "path": "/widgetjsonrpctable/{item_id}", "method": "DELETE", "item_id": item_id})
