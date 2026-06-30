from __future__ import annotations
from typing import Any
from pyspark.sql import SparkSession

from tigrbl_base._base import EngineSessionBase


class PySparkSession(EngineSessionBase):
    """Optional thin wrapper around SparkSession used by the plugin."""

    def __init__(self, spark: SparkSession) -> None:
        super().__init__()
        self.spark = spark

    def sql(self, query: str, *args: Any, **kwargs: Any):
        return self.spark.sql(query, *args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.spark, name)

    async def _tx_begin_impl(self) -> None:
        return

    async def _tx_commit_impl(self) -> None:
        return

    async def _tx_rollback_impl(self) -> None:
        return

    def _add_impl(self, obj: Any) -> Any:
        raise NotImplementedError("PySparkSession does not implement ORM add(obj)")

    async def _delete_impl(self, obj: Any) -> None:
        raise NotImplementedError("PySparkSession does not implement ORM delete(obj)")

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        return None

    async def _execute_impl(self, stmt: Any) -> Any:
        if isinstance(stmt, str):
            return self.sql(stmt)
        raise NotImplementedError("PySparkSession execute expects a SQL string")

    async def _executeloop_impl(self, statements: Any) -> list[Any]:
        return [await self._execute_impl(stmt) for stmt in statements]

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise NotImplementedError("PySparkSession does not implement executemany")

    async def _close_impl(self) -> None:
        # Intentionally a no-op by default. Users may stop the session explicitly if desired.
        return


__all__ = ["PySparkSession"]
