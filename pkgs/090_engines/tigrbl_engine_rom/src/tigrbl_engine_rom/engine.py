from __future__ import annotations

from copy import deepcopy
from types import MappingProxyType
from typing import Any, Iterable, Mapping

from tigrbl_base._base import EngineBase


def _freeze(value: Any) -> Any:
    """Return an immutable, detached representation of configuration data."""
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    return deepcopy(value)


def _thaw(value: Any) -> Any:
    """Return a caller-owned copy of a frozen value."""
    if isinstance(value, Mapping):
        return {key: _thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return {_thaw(item) for item in value}
    return deepcopy(value)


class ROMEngine(EngineBase):
    """Process-local immutable row image bound as an input to one table."""

    def __init__(
        self,
        rows: Iterable[Mapping[str, Any]] | None = None,
        *,
        primary_key: str = "id",
        namespace: str = "default",
        spec: Any = None,
    ) -> None:
        if not isinstance(namespace, str) or not namespace:
            raise ValueError("namespace must be a non-empty string")
        if not isinstance(primary_key, str) or not primary_key:
            raise ValueError("primary_key must be a non-empty string")
        self.namespace = namespace
        self.spec = spec
        self.primary_key = primary_key
        frozen_rows: list[Mapping[str, Any]] = []
        index: dict[Any, Mapping[str, Any]] = {}
        for position, source_row in enumerate(rows or ()):
            if not isinstance(source_row, Mapping):
                raise TypeError(f"row {position} must be a mapping")
            if primary_key not in source_row:
                raise ValueError(
                    f"row {position} is missing primary key {primary_key!r}"
                )
            key = deepcopy(source_row[primary_key])
            try:
                duplicate = key in index
            except TypeError as exc:
                raise TypeError(
                    f"primary key {primary_key!r} must be hashable"
                ) from exc
            if duplicate:
                raise ValueError(f"duplicate primary key {key!r}")
            frozen_row = _freeze(source_row)
            frozen_rows.append(frozen_row)
            index[key] = frozen_row

        self._rows = tuple(frozen_rows)
        self._index = MappingProxyType(index)

    def to_provider(self) -> "ROMEngine":
        """Expose this immutable engine as its own provider-like object."""
        return self

    async def _executeloop_impl(self, statements: Any) -> Any:
        from .session import ROMSession

        session = ROMSession(self)
        try:
            return await session.executeloop(statements)
        finally:
            await session.close()

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        from .session import ROMSession

        session = ROMSession(self)
        try:
            return await session.executemany(stmt, parameter_sets)
        finally:
            await session.close()

    def get(self, ident: Any) -> dict[str, Any] | None:
        row = self._index.get(ident)
        return None if row is None else _thaw(row)

    def scan(self) -> list[dict[str, Any]]:
        return [_thaw(row) for row in self._rows]


__all__ = ["ROMEngine"]
