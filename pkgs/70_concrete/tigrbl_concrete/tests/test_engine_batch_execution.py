from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from tigrbl_concrete._concrete._engine import Engine


class BatchSession:
    def __init__(self) -> None:
        self.closed = False

    def executeloop(self, statements):
        return [("loop", statement) for statement in statements]

    def executemany(self, stmt, parameter_sets):
        return ("many", stmt, parameter_sets)

    def close(self) -> None:
        self.closed = True


class NoBatchSession:
    def close(self) -> None:
        return None


@dataclass
class Provider:
    db: object
    kind: str = "sync"

    def ensure(self):
        return object(), lambda: self.db

    def session(self):
        return self.db

    def supports(self):
        return {"engine": "test"}

    @property
    def get_db(self):
        return lambda: self.db


def _engine_for(db: object) -> Engine:
    engine = object.__new__(Engine)
    engine.spec = SimpleNamespace(kind="test")
    engine.provider = Provider(db)
    return engine


@pytest.mark.asyncio
async def test_engine_delegates_batch_execution_to_session() -> None:
    engine = _engine_for(BatchSession())

    assert await engine.executeloop(["SELECT 1"]) == [("loop", "SELECT 1")]
    assert await engine.executemany("INSERT", [{"id": 1}]) == (
        "many",
        "INSERT",
        [{"id": 1}],
    )


@pytest.mark.asyncio
async def test_engine_batch_execution_raises_when_session_lacks_methods() -> None:
    engine = _engine_for(NoBatchSession())

    with pytest.raises(NotImplementedError, match="executeloop"):
        await engine.executeloop([])

    with pytest.raises(NotImplementedError, match="executemany"):
        await engine.executemany("INSERT", [])
