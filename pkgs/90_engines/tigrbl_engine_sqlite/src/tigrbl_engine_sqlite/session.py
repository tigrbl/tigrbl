from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy.orm import Session as _SASession
from tigrbl_concrete._concrete._engine_session import EngineSession
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec


class _SqliteAlchemySession(_SASession):
    def executeloop(self, statements: Iterable[Any]) -> list[Any]:
        results: list[Any] = []
        for item in statements:
            if (
                isinstance(item, tuple)
                and len(item) == 2
                and isinstance(item[1], (Mapping, list, tuple))
            ):
                results.append(self.execute(item[0], item[1]))
            else:
                results.append(self.execute(item))
        return results

    def executemany(self, stmt: Any, parameter_sets: Iterable[Mapping[str, Any]]) -> Any:
        return self.execute(stmt, list(parameter_sets))


class SqliteSession(EngineSession):
    """SQLite engine session exposed through the shared EngineSession contract."""

    def __init__(
        self, underlying: _SqliteAlchemySession, spec: EngineSessionSpec | None = None
    ) -> None:
        super().__init__(underlying, spec)


__all__ = ["SqliteSession"]
