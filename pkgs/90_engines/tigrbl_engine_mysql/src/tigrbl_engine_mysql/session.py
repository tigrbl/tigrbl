from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy.orm import Session as _SASession
from tigrbl_concrete._concrete._engine_session import EngineSession
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec


class _MySQLAlchemySession(_SASession):
    def executeloop(self, statements: Iterable[Any]) -> list[Any]:
        results = []
        for item in statements:
            if isinstance(item, tuple) and len(item) == 2:
                results.append(self.execute(item[0], item[1]))
            else:
                results.append(self.execute(item))
        return results

    def executemany(self, stmt: Any, parameter_sets: Iterable[Mapping[str, Any]]) -> Any:
        return self.execute(stmt, list(parameter_sets))


class MySQLSession(EngineSession):
    """MySQL session exposed through Tigrbl's shared EngineSession contract."""

    def __init__(self, underlying: _MySQLAlchemySession, spec: EngineSessionSpec | None = None) -> None:
        super().__init__(underlying, spec or EngineSessionSpec())


__all__ = ["MySQLSession"]

