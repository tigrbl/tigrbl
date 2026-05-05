from __future__ import annotations

import pytest

from tigrbl_concrete._concrete._session import DefaultSession


class BatchUnderlying:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object, object | None]] = []

    def executeloop(self, statements):
        self.calls.append(("executeloop", statements, None))
        return [("loop", statement) for statement in statements]

    def executemany(self, stmt, parameter_sets):
        self.calls.append(("executemany", stmt, parameter_sets))
        return ("many", stmt, parameter_sets)


class AsyncBatchUnderlying:
    async def executeloop(self, statements):
        return [("async-loop", statement) for statement in statements]

    async def executemany(self, stmt, parameter_sets):
        return ("async-many", stmt, parameter_sets)


class NoBatchUnderlying:
    pass


@pytest.mark.asyncio
async def test_default_session_delegates_batch_execution_methods() -> None:
    underlying = BatchUnderlying()
    session = DefaultSession(underlying)

    assert await session.executeloop(["SELECT 1", "SELECT 2"]) == [
        ("loop", "SELECT 1"),
        ("loop", "SELECT 2"),
    ]
    assert await session.executemany("INSERT", [{"id": 1}]) == (
        "many",
        "INSERT",
        [{"id": 1}],
    )
    assert underlying.calls == [
        ("executeloop", ["SELECT 1", "SELECT 2"], None),
        ("executemany", "INSERT", [{"id": 1}]),
    ]


@pytest.mark.asyncio
async def test_default_session_awaits_async_batch_execution_methods() -> None:
    session = DefaultSession(AsyncBatchUnderlying())

    assert await session.executeloop(["SELECT 1"]) == [("async-loop", "SELECT 1")]
    assert await session.executemany("INSERT", [{"id": 1}]) == (
        "async-many",
        "INSERT",
        [{"id": 1}],
    )


@pytest.mark.asyncio
async def test_default_session_raises_for_missing_batch_execution_methods() -> None:
    session = DefaultSession(NoBatchUnderlying())

    with pytest.raises(NotImplementedError, match="executeloop"):
        await session.executeloop([])

    with pytest.raises(NotImplementedError, match="executemany"):
        await session.executemany("INSERT", [])
