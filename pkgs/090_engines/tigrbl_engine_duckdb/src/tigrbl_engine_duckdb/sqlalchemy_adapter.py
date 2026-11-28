from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


class DuckDBSqlAlchemyAdapter:
    """DuckDB SQLAlchemy session adapter wrapped by Tigrbl EngineSession."""

    def __init__(self, session: Any) -> None:
        self._session = session

    def begin(self) -> Any:
        return self._session.begin()

    def commit(self) -> Any:
        return self._session.commit()

    def rollback(self) -> Any:
        return self._session.rollback()

    def in_transaction(self) -> bool:
        return bool(self._session.in_transaction())

    def get_bind(self) -> Any:
        return self._session.get_bind()

    def add(self, obj: Any) -> Any:
        return self._session.add(obj)

    def delete(self, obj: Any) -> Any:
        return self._session.delete(obj)

    def flush(self) -> Any:
        return self._session.flush()

    def refresh(self, obj: Any) -> Any:
        return self._session.refresh(obj)

    def get(self, model: type, ident: Any) -> Any:
        return self._session.get(model, ident)

    def execute(self, stmt: Any) -> Any:
        return self._session.execute(stmt)

    def executeloop(self, statements: Iterable[Any]) -> list[Any]:
        results: list[Any] = []
        for item in statements:
            if (
                isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[1], (Mapping, list, tuple))
            ):
                results.append(self._session.execute(item[0], item[1]))
            else:
                results.append(self._session.execute(item))
        return results

    def executemany(self, stmt: Any, parameter_sets: Iterable[Mapping[str, Any]]) -> Any:
        return self._session.execute(stmt, list(parameter_sets))

    def close(self) -> Any:
        return self._session.close()


__all__ = ["DuckDBSqlAlchemyAdapter"]
