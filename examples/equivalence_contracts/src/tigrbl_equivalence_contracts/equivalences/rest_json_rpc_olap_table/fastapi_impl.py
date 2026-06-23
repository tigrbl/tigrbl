"""FastAPI route-surface implementation for Tigrbl RestJsonRpcOlapTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetrestjsonrpcolaptable")
def get_1() -> dict[str, str]:
    return {"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable", "method": "GET"}


@app.post("/widgetrestjsonrpcolaptable")
def post_2() -> dict[str, str]:
    return {"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable", "method": "POST"}


@app.get("/widgetrestjsonrpcolaptable/{item_id}")
def get_3(item_id: str) -> dict[str, str]:
    return {"table_class": "RestJsonRpcOlapTable", "path": "/widgetrestjsonrpcolaptable/{item_id}", "method": "GET", "item_id": item_id}
