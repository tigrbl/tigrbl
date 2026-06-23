"""FastAPI route-surface implementation for Tigrbl WebTransportServerStreamTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetwebtransportserverstreamtable")
def get_1() -> dict[str, str]:
    return {"table_class": "WebTransportServerStreamTable", "path": "/widgetwebtransportserverstreamtable", "method": "GET"}
