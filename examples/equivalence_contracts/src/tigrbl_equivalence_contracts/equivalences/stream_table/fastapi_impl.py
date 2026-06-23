"""FastAPI route-surface implementation for Tigrbl StreamTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetstreamtable")
def get_1() -> dict[str, str]:
    return {"table_class": "StreamTable", "path": "/widgetstreamtable", "method": "GET"}
