"""Flask route-surface implementation for Tigrbl JsonRpcBulkCrudTable."""

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


@app.get("/widgetjsonrpcbulkcrudtable")
def get_1():
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable", "method": "GET"})


@app.post("/widgetjsonrpcbulkcrudtable")
def post_2():
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable", "method": "POST"})


@app.patch("/widgetjsonrpcbulkcrudtable")
def patch_3():
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable", "method": "PATCH"})


@app.put("/widgetjsonrpcbulkcrudtable")
def put_4():
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable", "method": "PUT"})


@app.delete("/widgetjsonrpcbulkcrudtable")
def delete_5():
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable", "method": "DELETE"})


@app.get("/widgetjsonrpcbulkcrudtable/<item_id>")
def get_6(item_id: str):
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable/{item_id}", "method": "GET", "item_id": item_id})


@app.patch("/widgetjsonrpcbulkcrudtable/<item_id>")
def patch_7(item_id: str):
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable/{item_id}", "method": "PATCH", "item_id": item_id})


@app.put("/widgetjsonrpcbulkcrudtable/<item_id>")
def put_8(item_id: str):
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable/{item_id}", "method": "PUT", "item_id": item_id})


@app.delete("/widgetjsonrpcbulkcrudtable/<item_id>")
def delete_9(item_id: str):
    return jsonify({"table_class": "JsonRpcBulkCrudTable", "path": "/widgetjsonrpcbulkcrudtable/{item_id}", "method": "DELETE", "item_id": item_id})
