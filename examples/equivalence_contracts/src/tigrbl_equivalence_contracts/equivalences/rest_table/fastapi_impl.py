"""FastAPI route-surface implementation for Tigrbl RestTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetresttable")
def get_1() -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable", "method": "GET"}


@app.post("/widgetresttable")
def post_2() -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable", "method": "POST"}


@app.delete("/widgetresttable")
def delete_3() -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable", "method": "DELETE"}


@app.get("/widgetresttable/{item_id}")
def get_4(item_id: str) -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable/{item_id}", "method": "GET", "item_id": item_id}


@app.patch("/widgetresttable/{item_id}")
def patch_5(item_id: str) -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable/{item_id}", "method": "PATCH", "item_id": item_id}


@app.put("/widgetresttable/{item_id}")
def put_6(item_id: str) -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable/{item_id}", "method": "PUT", "item_id": item_id}


@app.delete("/widgetresttable/{item_id}")
def delete_7(item_id: str) -> dict[str, str]:
    return {"table_class": "RestTable", "path": "/widgetresttable/{item_id}", "method": "DELETE", "item_id": item_id}
