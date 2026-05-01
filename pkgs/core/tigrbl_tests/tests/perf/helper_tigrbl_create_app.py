from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path
from typing import Any

from tigrbl import TableBase, TigrblApp
from tigrbl.factories.engine import sqlitef
from tigrbl.types import Column, Integer, String


def _build_benchmark_item_model() -> type[TableBase]:
    class TigrblBenchmarkItem(TableBase):
        __tablename__ = "benchmark_item"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

    return TigrblBenchmarkItem


def create_tigrbl_app(db_path: Path) -> TigrblApp:
    """Build a Tigrbl app with a single create command endpoint."""
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False))
    benchmark_model = _build_benchmark_item_model()
    app.include_table(benchmark_model)
    return app


async def initialize_tigrbl_app(app: TigrblApp) -> None:
    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    app.mount_jsonrpc(prefix="/rpc")


async def dispose_tigrbl_app(app: TigrblApp) -> None:
    engine = getattr(app, "engine", None)
    provider = getattr(engine, "provider", None)
    raw_engine = getattr(provider, "_engine", None)
    dispose = getattr(raw_engine, "dispose", None)
    if not callable(dispose):
        return
    result: Any = dispose()
    if inspect.isawaitable(result):
        await result


def fetch_tigrbl_names(db_path: Path) -> list[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM benchmark_item ORDER BY id"
        ).fetchall()
    return [row[0] for row in rows]


def tigrbl_create_path() -> str:
    return "/tigrblbenchmarkitem"


def tigrbl_create_rpc_method() -> str:
    return "TigrblBenchmarkItem.create"

