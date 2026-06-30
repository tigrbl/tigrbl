from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from sqlalchemy.orm import Session as _SASession


class PostgresSession(_SASession):
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
