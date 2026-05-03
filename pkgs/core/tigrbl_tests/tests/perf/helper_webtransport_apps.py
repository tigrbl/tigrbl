from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from tigrbl import WebTransportBindingSpec
from tigrbl_concrete._concrete._app import App as TigrblApp


def _ensure_webtransport_items_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmark_webtransport_item (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        conn.commit()


def fetch_webtransport_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_webtransport_item ORDER BY id"
        ).fetchall()
    return [str(row[0]) for row in rows]


def _message_text(ctx: Any) -> str:
    getter = getattr(ctx, "get", None)
    message = getter("channel_message") if callable(getter) else None
    if isinstance(message, dict):
        text = message.get("text")
        if isinstance(text, str):
            return text
        raw = message.get("bytes")
        if isinstance(raw, (bytes, bytearray)):
            return bytes(raw).decode("utf-8")
    body = getter("body") if callable(getter) else None
    if isinstance(body, bytes):
        return body.decode("utf-8")
    if isinstance(body, bytearray):
        return bytes(body).decode("utf-8")
    return ""


def create_tigrbl_webtransport_transport_app(db_path: Path) -> TigrblApp:
    del db_path
    app = TigrblApp(title="Tigrbl WebTransport Transport Benchmark")

    async def echo_transport(ctx: Any) -> str:
        return _message_text(ctx)

    app.add_route(
        "/transport/echo",
        echo_transport,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/transport/echo",
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    return app


def create_tigrbl_webtransport_db_app(db_path: Path) -> TigrblApp:
    _ensure_webtransport_items_db(db_path)
    app = TigrblApp(title="Tigrbl WebTransport DB Benchmark")

    async def create_item_transport(ctx: Any) -> dict[str, Any]:
        payload = json.loads(_message_text(ctx))
        name = str(payload["name"])
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO benchmark_webtransport_item(name) VALUES(?)",
                (name,),
            )
            conn.commit()
            item_id = int(cursor.lastrowid or 0)
        return {"id": item_id, "name": name}

    app.add_route(
        "/transport/items",
        create_item_transport,
        methods=("POST",),
        tigrbl_binding=WebTransportBindingSpec(
            proto="webtransport",
            path="/transport/items",
        ),
        tigrbl_exchange="bidirectional_stream",
    )
    return app
