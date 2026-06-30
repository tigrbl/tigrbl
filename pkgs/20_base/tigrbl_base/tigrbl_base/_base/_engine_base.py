from __future__ import annotations

from typing import Any


class EngineBase:
    """Base contract for concrete engine façade implementations."""

    spec: Any

    def to_provider(self) -> Any:  # pragma: no cover - interface contract
        raise NotImplementedError

    async def executeloop(self, statements: Any) -> Any:
        return await self._executeloop_impl(statements)

    async def executemany(self, stmt: Any, parameter_sets: Any) -> Any:
        return await self._executemany_impl(stmt, parameter_sets)

    async def _executeloop_impl(self, statements: Any) -> Any:
        raise NotImplementedError

    async def _executemany_impl(self, stmt: Any, parameter_sets: Any) -> Any:
        raise NotImplementedError


__all__ = ["EngineBase"]
