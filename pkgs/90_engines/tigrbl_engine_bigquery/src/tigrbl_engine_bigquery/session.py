from __future__ import annotations
from typing import Any

from tigrbl_base._base import EngineSessionBase


class BigQuerySession(EngineSessionBase):
    """Represents a logical unit of work against BigQuery.

    This wrapper is intentionally lightweight. It can be extended to integrate
    with your app's patterns (e.g., typed query helpers).

    Example
    -------
    >>> s = BigQuerySession(engine)
    >>> # rows = s.query("SELECT 1")   # requires google-cloud-bigquery installed & configured
    """

    def __init__(self, engine: Any) -> None:
        super().__init__()
        self.engine = engine
        self._client = None  # lazy

    # Optional: context manager
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self._close_client()

    @property
    def client(self):
        """Lazily create a BigQuery client when first used."""
        if self._client is None:
            from google.cloud import bigquery  # heavy import delayed

            self._client = bigquery.Client(
                project=self.engine.project, **self.engine.kwargs
            )
        return self._client

    def query(self, sql: str, **job_config_kwargs):
        """Execute a SQL query and return the BigQuery ResultIterator.

        Notes
        -----
        - This method is a convenience for quick experiments. Production code
          should add schemas, timeouts, and retries as appropriate.
        """
        from google.cloud import bigquery

        job_config = (
            bigquery.QueryJobConfig(**job_config_kwargs) if job_config_kwargs else None
        )
        job = self.client.query(sql, job_config=job_config)
        return job.result()

    async def _tx_begin_impl(self) -> None:
        return

    async def _tx_commit_impl(self) -> None:
        return

    async def _tx_rollback_impl(self) -> None:
        return

    def _add_impl(self, obj: Any) -> Any:
        raise NotImplementedError("BigQuerySession does not implement ORM add(obj)")

    async def _delete_impl(self, obj: Any) -> None:
        raise NotImplementedError("BigQuerySession does not implement ORM delete(obj)")

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        return None

    async def _execute_impl(self, stmt: Any) -> Any:
        if isinstance(stmt, str):
            return self.query(stmt)
        raise NotImplementedError("BigQuerySession execute expects a SQL string")

    async def _executeloop_impl(self, statements: Any) -> list[Any]:
        return [await self._execute_impl(stmt) for stmt in statements]

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise NotImplementedError("BigQuerySession does not implement executemany")

    def _close_client(self) -> None:
        try:
            if self._client is not None:
                self._client.close()
        finally:
            self._client = None

    async def _close_impl(self) -> None:
        self._close_client()


__all__ = ["BigQuerySession"]
