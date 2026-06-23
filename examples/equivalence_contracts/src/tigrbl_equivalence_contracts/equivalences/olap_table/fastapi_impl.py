"""FastAPI route-surface implementation for Tigrbl OlapTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetolaptable")
def get_1() -> dict[str, str]:
    return {"table_class": "OlapTable", "path": "/widgetolaptable", "method": "GET"}


@app.post("/widgetolaptable")
def post_2() -> dict[str, str]:
    return {"table_class": "OlapTable", "path": "/widgetolaptable", "method": "POST"}


@app.get("/widgetolaptable/{item_id}")
def get_3(item_id: str) -> dict[str, str]:
    return {"table_class": "OlapTable", "path": "/widgetolaptable/{item_id}", "method": "GET", "item_id": item_id}
