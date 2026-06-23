"""FastAPI route-surface implementation for Tigrbl WebSocketTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetwebsockettable")
def get_1() -> dict[str, str]:
    return {"table_class": "WebSocketTable", "path": "/widgetwebsockettable", "method": "GET"}


@app.post("/widgetwebsockettable")
def post_2() -> dict[str, str]:
    return {"table_class": "WebSocketTable", "path": "/widgetwebsockettable", "method": "POST"}
