"""Flask route-surface implementation for Tigrbl WebTransportBidiTable."""

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


@app.get("/widgetwebtransportbiditable")
def get_1():
    return jsonify({"table_class": "WebTransportBidiTable", "path": "/widgetwebtransportbiditable", "method": "GET"})


@app.post("/widgetwebtransportbiditable")
def post_2():
    return jsonify({"table_class": "WebTransportBidiTable", "path": "/widgetwebtransportbiditable", "method": "POST"})
