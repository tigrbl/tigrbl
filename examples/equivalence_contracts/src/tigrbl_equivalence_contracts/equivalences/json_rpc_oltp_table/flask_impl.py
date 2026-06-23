"""Flask route-surface implementation for Tigrbl JsonRpcOltpTable."""

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


@app.get("/widgetjsonrpcoltptable")
def get_1():
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable", "method": "GET"})


@app.post("/widgetjsonrpcoltptable")
def post_2():
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable", "method": "POST"})


@app.get("/widgetjsonrpcoltptable/<item_id>")
def get_3(item_id: str):
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetjsonrpcoltptable/<item_id>")
def patch_4(item_id: str):
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetjsonrpcoltptable/<item_id>")
def put_5(item_id: str):
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetjsonrpcoltptable/<item_id>")
def delete_6(item_id: str):
    return jsonify({"table_class": "JsonRpcOltpTable", "path": "/widgetjsonrpcoltptable/{item_id}", "method": "DELETE", "item_id": item_id})
