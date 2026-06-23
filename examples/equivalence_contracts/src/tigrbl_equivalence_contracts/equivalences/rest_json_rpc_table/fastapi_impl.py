"""FastAPI route-surface implementation for Tigrbl RestJsonRpcTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetrestjsonrpctable")
def get_1() -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable", "method": "GET"}


@app.post("/widgetrestjsonrpctable")
def post_2() -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable", "method": "POST"}


@app.delete("/widgetrestjsonrpctable")
def delete_3() -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable", "method": "DELETE"}


@app.get("/widgetrestjsonrpctable/{item_id}")
def get_4(item_id: str) -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable/{item_id}", "method": "GET", "item_id": item_id}


@app.patch("/widgetrestjsonrpctable/{item_id}")
def patch_5(item_id: str) -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable/{item_id}", "method": "PATCH", "item_id": item_id}


@app.put("/widgetrestjsonrpctable/{item_id}")
def put_6(item_id: str) -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable/{item_id}", "method": "PUT", "item_id": item_id}


@app.delete("/widgetrestjsonrpctable/{item_id}")
def delete_7(item_id: str) -> dict[str, str]:
    return {"table_class": "RestJsonRpcTable", "path": "/widgetrestjsonrpctable/{item_id}", "method": "DELETE", "item_id": item_id}
