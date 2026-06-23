"""FastAPI route-surface implementation for Tigrbl JsonRpcOlapTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetjsonrpcolaptable")
def get_1() -> dict[str, str]:
    return {"table_class": "JsonRpcOlapTable", "path": "/widgetjsonrpcolaptable", "method": "GET"}


@app.post("/widgetjsonrpcolaptable")
def post_2() -> dict[str, str]:
    return {"table_class": "JsonRpcOlapTable", "path": "/widgetjsonrpcolaptable", "method": "POST"}


@app.get("/widgetjsonrpcolaptable/{item_id}")
def get_3(item_id: str) -> dict[str, str]:
    return {"table_class": "JsonRpcOlapTable", "path": "/widgetjsonrpcolaptable/{item_id}", "method": "GET", "item_id": item_id}
