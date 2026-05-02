from __future__ import annotations

import inspect
import json
import sqlite3
from pathlib import Path

from fastapi import FastAPI, WebSocket
from tigrbl_concrete._concrete._app import App as TigrblApp


def _ensure_websocket_items_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmark_ws_item (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        conn.commit()


def fetch_websocket_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_ws_item ORDER BY id"
        ).fetchall()
    return [str(row[0]) for row in rows]


def create_tigrbl_websocket_transport_app(db_path: Path) -> TigrblApp:
    del db_path
    app = TigrblApp(title="Tigrbl WebSocket Transport Benchmark")

    @app.websocket("/ws/echo")
    async def echo_socket(ws) -> None:
        text = await ws.receive_text()
        return text

    return app


def create_tigrbl_websocket_db_app(db_path: Path) -> TigrblApp:
    _ensure_websocket_items_db(db_path)
    app = TigrblApp(title="Tigrbl WebSocket DB Benchmark")

    @app.websocket("/ws/items")
    async def create_item_socket(ws) -> None:
        payload = json.loads(await ws.receive_text())
        name = str(payload["name"])
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO benchmark_ws_item(name) VALUES(?)",
                (name,),
            )
            conn.commit()
            item_id = int(cursor.lastrowid or 0)
        return {"id": item_id, "name": name}

    return app


def create_tigrbl_websocket_app(db_path: Path) -> TigrblApp:
    return create_tigrbl_websocket_db_app(db_path)


async def initialize_tigrbl_websocket_app(app: TigrblApp) -> None:
    init = getattr(app, "initialize", None)
    if not callable(init):
        return
    init_result = init()
    if inspect.isawaitable(init_result):
        await init_result


async def dispose_tigrbl_websocket_app(app: TigrblApp) -> None:
    engine = getattr(app, "engine", None)
    provider = getattr(engine, "provider", None)
    raw_engine = getattr(provider, "_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    result = dispose()
    if inspect.isawaitable(result):
        await result


def create_fastapi_websocket_transport_app(db_path: Path) -> FastAPI:
    del db_path
    app = FastAPI()

    @app.websocket("/ws/echo")
    async def echo_socket(ws: WebSocket) -> None:
        await ws.accept()
        text = await ws.receive_text()
        await ws.send_text(text)
        await ws.close()

    return app


def create_fastapi_websocket_db_app(db_path: Path) -> FastAPI:
    _ensure_websocket_items_db(db_path)
    app = FastAPI()

    @app.websocket("/ws/items")
    async def create_item_socket(ws: WebSocket) -> None:
        await ws.accept()
        payload = json.loads(await ws.receive_text())
        name = str(payload["name"])
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO benchmark_ws_item(name) VALUES(?)",
                (name,),
            )
            conn.commit()
            item_id = int(cursor.lastrowid or 0)
        await ws.send_text(
            json.dumps({"id": item_id, "name": name}, separators=(",", ":"))
        )
        await ws.close()

    return app


def create_fastapi_websocket_app(db_path: Path) -> FastAPI:
    return create_fastapi_websocket_db_app(db_path)
