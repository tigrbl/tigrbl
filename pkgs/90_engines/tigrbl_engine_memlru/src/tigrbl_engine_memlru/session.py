from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from sqlalchemy.orm.exc import NoResultFound

from tigrbl_base._base import EngineSessionBase

from .lru import LRUCache

_MISSING = object()


class LRUSession(EngineSessionBase):
    """EngineSessionBase adapter plus native record operations for MemLRU."""

    def __init__(self, engine: LRUCache) -> None:
        super().__init__()
        self._engine = engine
        self._closed = False

    async def _tx_begin_impl(self) -> None:
        return

    async def _tx_commit_impl(self) -> None:
        return

    async def _tx_rollback_impl(self) -> None:
        return

    async def _close_impl(self) -> None:
        self._closed = True

    def put(self, key: str, value: Any, *, cost: float | None = None) -> None:
        self._require_not_closed()
        self._engine.set(self._require_key(key), value, cost=cost)
        self._dirty = True

    def lookup(self, key: str, default: Any = None) -> Any:
        self._require_not_closed()
        return self._engine.get(self._require_key(key), default)

    def remove(self, key: str) -> bool:
        self._require_not_closed()
        removed = self._engine.delete(self._require_key(key))
        self._dirty = self._dirty or removed
        return removed

    def clear_cache(self) -> None:
        self._require_not_closed()
        self._engine.clear()
        self._dirty = True

    def stats(self) -> dict[str, Any]:
        self._require_not_closed()
        return self._engine.stats()

    def create_record(self, model: type, data: Mapping[str, Any]) -> Any:
        key = self._require_key(data.get("key"))
        if "value" not in data:
            raise ValueError("value is required")
        cost = self._normalize_cost(data.get("cost"))
        self.put(key, data["value"], cost=cost)
        return model(key=key, value=data["value"], cost=cost)

    def read_record(self, model: type, ident: Any) -> Any:
        key = self._require_key(ident)
        entry = self._engine.get_entry(key, _MISSING)
        if entry is _MISSING:
            raise NoResultFound(f"{model.__name__}({key!r}) not found")
        value, cost = entry
        return model(key=key, value=value, cost=cost)

    def delete_record(self, model: type, ident: Any) -> dict[str, int]:
        key = self._require_key(ident)
        if not self.remove(key):
            raise NoResultFound(f"{model.__name__}({key!r}) not found")
        return {"deleted": 1}

    def list_records(
        self,
        model: type,
        *,
        filters: Mapping[str, Any] | None = None,
        skip: int | None = None,
        limit: int | None = None,
        sort: Sequence[str] | str | None = None,
    ) -> list[Any]:
        self._require_not_closed()
        if sort:
            raise ValueError("MemLRU list order is fixed from least to most recent")
        selected = [
            row
            for row in self._engine.snapshot()
            if self._matches(row, filters or {})
        ]
        start = max(skip or 0, 0)
        stop = None if limit is None else start + max(limit, 0)
        return [model(**row) for row in selected[start:stop]]

    def clear_records(
        self,
        model: type,
        *,
        filters: Mapping[str, Any] | None = None,
    ) -> dict[str, int]:
        del model
        selected = [
            row["key"]
            for row in self._engine.snapshot()
            if self._matches(row, filters or {})
        ]
        for key in selected:
            self.remove(key)
        return {"deleted": len(selected)}

    def count_records(
        self,
        model: type,
        *,
        filters: Mapping[str, Any] | None = None,
    ) -> dict[str, int]:
        del model
        count = sum(
            self._matches(row, filters or {}) for row in self._engine.snapshot()
        )
        return {"count": count}

    def exists_record(self, model: type, ident: Any) -> dict[str, bool]:
        del model
        key = self._require_key(ident)
        return {"exists": self._engine.get_entry(key, _MISSING) is not _MISSING}

    def _add_impl(self, obj: Any) -> None:
        self.create_record(
            type(obj),
            {
                "key": getattr(obj, "key"),
                "value": getattr(obj, "value"),
                "cost": getattr(obj, "cost", None),
            },
        )

    async def _delete_impl(self, obj: Any) -> None:
        self.delete_record(type(obj), getattr(obj, "key"))

    async def _get_impl(self, model: type, ident: Any) -> Any | None:
        try:
            return self.read_record(model, ident)
        except NoResultFound:
            return None

    async def _execute_impl(self, stmt: Any) -> Any:
        del stmt
        raise TypeError("MemLRU sessions do not execute SQL statements")

    async def _executeloop_impl(self, statements: Any) -> Any:
        del statements
        raise TypeError("MemLRU sessions do not execute SQL statement batches")

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        del stmt, parameter_sets
        raise TypeError("MemLRU sessions do not execute SQL statement batches")

    def _require_not_closed(self) -> None:
        if self._closed:
            raise RuntimeError("session is closed")

    @staticmethod
    def _require_key(value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("key must be a non-empty string")
        return value

    @staticmethod
    def _normalize_cost(value: Any) -> float | None:
        if value is None:
            return None
        cost = float(value)
        if cost <= 0:
            raise ValueError("cost must be greater than zero")
        return cost

    @staticmethod
    def _matches(row: Mapping[str, Any], filters: Mapping[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in filters.items())


class AsyncLRUSession(LRUSession):
    """Deprecated compatibility name; LRUSession already has async lifecycle."""
