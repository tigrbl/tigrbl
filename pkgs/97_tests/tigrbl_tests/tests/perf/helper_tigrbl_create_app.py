from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path
from typing import Any, Mapping

from tigrbl import TableBase, TigrblApp
from tigrbl._spec import HttpJsonRpcBindingSpec, HttpRestBindingSpec, OpSpec
from tigrbl.factories.engine import sqlitef
from tigrbl.types import Column, Integer, String


def _build_benchmark_item_model(
    *, batch: Mapping[str, Any] | None = None
) -> type[TableBase]:
    batch_policy = dict(batch) if isinstance(batch, Mapping) else None

    class TigrblBenchmarkItem(TableBase):
        __tablename__ = "benchmark_item"
        __allow_unmapped__ = True

        id = Column(Integer, primary_key=True, autoincrement=True)
        name = Column(String, nullable=False)

        __tigrbl_ops__ = (
            OpSpec(
                alias="BenchmarkItem.create",
                target="create",
                batch=batch_policy,
                bindings=(
                    HttpRestBindingSpec(
                        proto="http.rest",
                        methods=("POST",),
                        path="/items",
                    ),
                    HttpJsonRpcBindingSpec(
                        proto="http.jsonrpc",
                        rpc_method="BenchmarkItem.create",
                    ),
                ),
            ),
        )

    return TigrblBenchmarkItem


def create_tigrbl_app(db_path: Path) -> TigrblApp:
    """Build a Tigrbl app with a single create command endpoint."""
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False), mount_system=False)
    benchmark_model = _build_benchmark_item_model()
    app.include_table(benchmark_model)
    return app


def create_tigrbl_batch_app(
    db_path: Path,
    *,
    max_size: int = 25,
    max_delay_ms: int = 1,
) -> TigrblApp:
    """Build the create benchmark app with batch policy enabled on create."""
    app = TigrblApp(engine=sqlitef(str(db_path), async_=False), mount_system=False)
    benchmark_model = _build_benchmark_item_model(
        batch={
            "enabled": True,
            "max_size": max_size,
            "max_delay_ms": max_delay_ms,
            "conflict_policy": "single_fallback",
            "overflow_policy": "backpressure",
            "result_fanout": "by_admission",
        }
    )
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
    return "/items"


def tigrbl_create_rpc_method() -> str:
    return "BenchmarkItem.create"

