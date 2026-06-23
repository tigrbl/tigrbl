"""FastAPI route-surface implementation for Tigrbl WebTransportClientStreamTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/widgetwebtransportclientstreamtable")
def post_1() -> dict[str, str]:
    return {"table_class": "WebTransportClientStreamTable", "path": "/widgetwebtransportclientstreamtable", "method": "POST"}
