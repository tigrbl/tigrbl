from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from tigrbl import EventStreamResponse, SseBindingSpec
from tigrbl_concrete._concrete._app import App as TigrblApp

SSE_EVENT_COUNT = 8
SSE_ROW_COUNT = 24


def _encode_sse_event(event: Any) -> bytes:
    if isinstance(event, (bytes, bytearray, memoryview)):
        payload = bytes(event)
        return payload if payload.endswith(b"\n\n") else payload + b"\n\n"
    if isinstance(event, str):
        return f"data: {event}\n\n".encode("utf-8")
    if isinstance(event, dict):
        lines: list[str] = []
        event_name = event.get("event")
        if event_name is not None:
            lines.append(f"event: {event_name}")
        event_id = event.get("id")
        if event_id is not None:
            lines.append(f"id: {event_id}")
        retry = event.get("retry")
        if retry is not None:
            lines.append(f"retry: {retry}")
        data = event.get("data")
        if data is None:
            lines.append("data:")
        elif isinstance(data, str):
            for part in data.splitlines() or [data]:
                lines.append(f"data: {part}")
        else:
            lines.append(
                f"data: {json.dumps(data, separators=(',', ':'), ensure_ascii=False)}"
            )
        return ("\n".join(lines) + "\n\n").encode("utf-8")
    return (
        f"data: {json.dumps(event, separators=(',', ':'), ensure_ascii=False)}\n\n"
    ).encode("utf-8")


def _transport_events() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "event": "message",
            "id": idx + 1,
            "data": {"chunk": idx, "source": "sse"},
        }
        for idx in range(SSE_EVENT_COUNT)
    )


def _ensure_sse_items_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmark_sse_item (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        existing = conn.execute("SELECT COUNT(*) FROM benchmark_sse_item").fetchone()
        if existing and int(existing[0]) >= SSE_ROW_COUNT:
            return
        conn.execute("DELETE FROM benchmark_sse_item")
        conn.executemany(
            "INSERT INTO benchmark_sse_item(name) VALUES(?)",
            [(f"sse-item-{idx}",) for idx in range(SSE_ROW_COUNT)],
        )
        conn.commit()


def expected_transport_sse_bytes() -> bytes:
    return b"".join(_encode_sse_event(event) for event in _transport_events())


def expected_db_sse_bytes() -> bytes:
    return b"".join(
        _encode_sse_event({"data": {"id": idx + 1, "name": f"sse-item-{idx}"}})
        for idx in range(SSE_ROW_COUNT)
    )


def create_tigrbl_sse_transport_app(db_path: Path) -> TigrblApp:
    del db_path
    app = TigrblApp(title="Tigrbl SSE Transport Benchmark")

    def fixed_events() -> EventStreamResponse:
        return EventStreamResponse(_transport_events())

    app.add_route(
        "/events/fixed",
        fixed_events,
        methods=("GET",),
        tigrbl_binding=SseBindingSpec(
            proto="http.sse",
            path="/events/fixed",
            methods=("GET",),
        ),
        tigrbl_exchange="event_stream",
    )
    return app


def create_tigrbl_sse_db_app(db_path: Path) -> TigrblApp:
    _ensure_sse_items_db(db_path)
    app = TigrblApp(title="Tigrbl SSE DB Benchmark")

    def db_events() -> EventStreamResponse:
        def _iter() -> Any:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT id, name FROM benchmark_sse_item ORDER BY id"
                )
                for item_id, name in rows:
                    yield {"data": {"id": int(item_id), "name": str(name)}}

        return EventStreamResponse(_iter())

    app.add_route(
        "/events/items",
        db_events,
        methods=("GET",),
        tigrbl_binding=SseBindingSpec(
            proto="http.sse",
            path="/events/items",
            methods=("GET",),
        ),
        tigrbl_exchange="event_stream",
    )
    return app


def create_fastapi_sse_transport_app(db_path: Path) -> FastAPI:
    del db_path
    app = FastAPI()

    @app.get("/events/fixed")
    def fixed_events() -> FastAPIStreamingResponse:
        return FastAPIStreamingResponse(
            (_encode_sse_event(event) for event in _transport_events()),
            media_type="text/event-stream",
            headers={"cache-control": "no-cache"},
        )

    return app


def create_fastapi_sse_db_app(db_path: Path) -> FastAPI:
    _ensure_sse_items_db(db_path)
    app = FastAPI()

    @app.get("/events/items")
    def db_events() -> FastAPIStreamingResponse:
        def _iter() -> Any:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT id, name FROM benchmark_sse_item ORDER BY id"
                )
                for item_id, name in rows:
                    yield _encode_sse_event(
                        {"data": {"id": int(item_id), "name": str(name)}}
                    )

        return FastAPIStreamingResponse(
            _iter(),
            media_type="text/event-stream",
            headers={"cache-control": "no-cache"},
        )

    return app
