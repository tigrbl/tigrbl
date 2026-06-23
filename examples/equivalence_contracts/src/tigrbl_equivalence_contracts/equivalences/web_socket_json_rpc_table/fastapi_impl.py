"""FastAPI route-surface implementation for Tigrbl WebSocketJsonRpcTable."""

from __future__ import annotations

from fastapi import FastAPI

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/widgetwebsocketjsonrpctable")
def get_1() -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable", "method": "GET"}


@app.post("/widgetwebsocketjsonrpctable")
def post_2() -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable", "method": "POST"}


@app.get("/widgetwebsocketjsonrpctable/{item_id}")
def get_3(item_id: str) -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable/{item_id}", "method": "GET", "item_id": item_id}


@app.patch("/widgetwebsocketjsonrpctable/{item_id}")
def patch_4(item_id: str) -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable/{item_id}", "method": "PATCH", "item_id": item_id}


@app.put("/widgetwebsocketjsonrpctable/{item_id}")
def put_5(item_id: str) -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable/{item_id}", "method": "PUT", "item_id": item_id}


@app.delete("/widgetwebsocketjsonrpctable/{item_id}")
def delete_6(item_id: str) -> dict[str, str]:
    return {"table_class": "WebSocketJsonRpcTable", "path": "/widgetwebsocketjsonrpctable/{item_id}", "method": "DELETE", "item_id": item_id}
