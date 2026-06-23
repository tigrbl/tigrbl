"""FastAPI route-surface implementation for Tigrbl WebTransportBidiTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetwebtransportbiditable")
def get_1() -> dict[str, str]:
    return {"table_class": "WebTransportBidiTable", "path": "/widgetwebtransportbiditable", "method": "GET"}


@app.post("/widgetwebtransportbiditable")
def post_2() -> dict[str, str]:
    return {"table_class": "WebTransportBidiTable", "path": "/widgetwebtransportbiditable", "method": "POST"}
