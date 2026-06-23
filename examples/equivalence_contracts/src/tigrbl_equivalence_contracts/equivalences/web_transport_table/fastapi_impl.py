"""FastAPI route-surface implementation for Tigrbl WebTransportTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetwebtransporttable")
def get_1() -> dict[str, str]:
    return {"table_class": "WebTransportTable", "path": "/widgetwebtransporttable", "method": "GET"}


@app.post("/widgetwebtransporttable")
def post_2() -> dict[str, str]:
    return {"table_class": "WebTransportTable", "path": "/widgetwebtransporttable", "method": "POST"}
