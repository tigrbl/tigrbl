"""FastAPI route-surface implementation for Tigrbl SseTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetssetable")
def get_1() -> dict[str, str]:
    return {"table_class": "SseTable", "path": "/widgetssetable", "method": "GET"}
