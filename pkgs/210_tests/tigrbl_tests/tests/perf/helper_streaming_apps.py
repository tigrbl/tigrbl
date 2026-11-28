from __future__ import annotations

import inspect
import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.responses import StreamingResponse as FastAPIStreamingResponse
from tigrbl_concrete._concrete._app import App as TigrblApp
from tigrbl_concrete._concrete._streaming_response import StreamingResponse

STREAM_CHUNK_COUNT = 8
STREAM_ROW_COUNT = 24


def _transport_chunks() -> tuple[bytes, ...]:
    return tuple(
        json.dumps(
            {"chunk": idx, "source": "stream"},
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
        for idx in range(STREAM_CHUNK_COUNT)
    )


def _ensure_stream_items_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS benchmark_stream_item (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        existing = conn.execute(
            "SELECT COUNT(*) FROM benchmark_stream_item"
        ).fetchone()
        if existing and int(existing[0]) >= STREAM_ROW_COUNT:
            return
        conn.execute("DELETE FROM benchmark_stream_item")
        conn.executemany(
            "INSERT INTO benchmark_stream_item(name) VALUES(?)",
            [(f"stream-item-{idx}",) for idx in range(STREAM_ROW_COUNT)],
        )
        conn.commit()


def expected_transport_stream_bytes() -> bytes:
    return b"".join(_transport_chunks())


def expected_db_stream_bytes() -> bytes:
    return b"".join(
        json.dumps(
            {"id": idx + 1, "name": f"stream-item-{idx}"},
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
        for idx in range(STREAM_ROW_COUNT)
    )


def create_tigrbl_streaming_transport_app(db_path: Path) -> TigrblApp:
    del db_path
    app = TigrblApp(title="Tigrbl Streaming Transport Benchmark")

    @app.get("/stream/fixed")
    def fixed_stream() -> StreamingResponse:
        return StreamingResponse(
            _transport_chunks(),
            media_type="application/x-ndjson",
        )

    return app


def create_tigrbl_streaming_db_app(db_path: Path) -> TigrblApp:
    _ensure_stream_items_db(db_path)
    app = TigrblApp(title="Tigrbl Streaming DB Benchmark")

    @app.get("/stream/items")
    def db_stream() -> StreamingResponse:
        def _iter() -> Any:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT id, name FROM benchmark_stream_item ORDER BY id"
                )
                for item_id, name in rows:
                    yield (
                        json.dumps(
                            {"id": int(item_id), "name": str(name)},
                            separators=(",", ":"),
                        ).encode("utf-8")
                        + b"\n"
                    )

        return StreamingResponse(_iter(), media_type="application/x-ndjson")

    return app


def create_tigrbl_streaming_app(db_path: Path) -> TigrblApp:
    return create_tigrbl_streaming_db_app(db_path)


async def initialize_tigrbl_streaming_app(app: TigrblApp) -> None:
    init = getattr(app, "initialize", None)
    if not callable(init):
        return
    init_result = init()
    if inspect.isawaitable(init_result):
        await init_result


async def dispose_tigrbl_streaming_app(app: TigrblApp) -> None:
    engine = getattr(app, "engine", None)
    provider = getattr(engine, "provider", None)
    raw_engine = getattr(provider, "_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    result: Any = dispose()
    if inspect.isawaitable(result):
        await result


def create_fastapi_streaming_transport_app(db_path: Path) -> FastAPI:
    del db_path
    app = FastAPI()

    @app.get("/stream/fixed")
    def fixed_stream() -> FastAPIStreamingResponse:
        return FastAPIStreamingResponse(
            _transport_chunks(),
            media_type="application/x-ndjson",
        )

    return app


def create_fastapi_streaming_db_app(db_path: Path) -> FastAPI:
    _ensure_stream_items_db(db_path)
    app = FastAPI()

    @app.get("/stream/items")
    def db_stream() -> FastAPIStreamingResponse:
        def _iter() -> Any:
            with sqlite3.connect(db_path) as conn:
                rows = conn.execute(
                    "SELECT id, name FROM benchmark_stream_item ORDER BY id"
                )
                for item_id, name in rows:
                    yield (
                        json.dumps(
                            {"id": int(item_id), "name": str(name)},
                            separators=(",", ":"),
                        ).encode("utf-8")
                        + b"\n"
                    )

        return FastAPIStreamingResponse(_iter(), media_type="application/x-ndjson")

    return app


def create_fastapi_streaming_app(db_path: Path) -> FastAPI:
    return create_fastapi_streaming_db_app(db_path)
