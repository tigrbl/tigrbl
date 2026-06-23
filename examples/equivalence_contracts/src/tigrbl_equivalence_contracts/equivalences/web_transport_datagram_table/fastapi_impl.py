"""FastAPI route-surface implementation for Tigrbl WebTransportDatagramTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/widgetwebtransportdatagramtable")
def post_1() -> dict[str, str]:
    return {"table_class": "WebTransportDatagramTable", "path": "/widgetwebtransportdatagramtable", "method": "POST"}
