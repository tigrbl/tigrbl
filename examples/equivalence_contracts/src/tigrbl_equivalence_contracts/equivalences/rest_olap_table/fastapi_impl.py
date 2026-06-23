"""FastAPI route-surface implementation for Tigrbl RestOlapTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetrestolaptable")
def get_1() -> dict[str, str]:
    return {"table_class": "RestOlapTable", "path": "/widgetrestolaptable", "method": "GET"}


@app.post("/widgetrestolaptable")
def post_2() -> dict[str, str]:
    return {"table_class": "RestOlapTable", "path": "/widgetrestolaptable", "method": "POST"}


@app.get("/widgetrestolaptable/{item_id}")
def get_3(item_id: str) -> dict[str, str]:
    return {"table_class": "RestOlapTable", "path": "/widgetrestolaptable/{item_id}", "method": "GET", "item_id": item_id}
