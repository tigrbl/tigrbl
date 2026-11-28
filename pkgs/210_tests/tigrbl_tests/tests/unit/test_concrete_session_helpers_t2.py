from __future__ import annotations

import pytest

from tigrbl_base._base._session_base import EngineSessionBase
from tigrbl_concrete._concrete._engine_session import EngineSession, wrap_sessionmaker
from tigrbl_core._spec.engine_session_spec import EngineSessionSpec


class RecordingSession:
    def __init__(self) -> None:
        self.events: list[object] = []
        self.open = False

    def begin(self) -> None:
        self.events.append("begin")
        self.open = True

    def commit(self) -> None:
        self.events.append("commit")
        self.open = False

    def rollback(self) -> None:
        self.events.append("rollback")
        self.open = False

    def in_transaction(self) -> bool:
        return self.open

    def add(self, obj: object) -> None:
        self.events.append(("add", obj))

    def delete(self, obj: object) -> None:
        self.events.append(("delete", obj))

    def flush(self) -> None:
        self.events.append("flush")

    def close(self) -> None:
        self.events.append("close")


@pytest.mark.asyncio
async def test_default_session_delegates_transaction_success_path() -> None:
    underlying = RecordingSession()
    session = EngineSession(underlying)

    await session.begin()
    session.add("item")
    await session.commit()

    assert underlying.events == ["begin", ("add", "item"), "flush", "commit"]
    assert session.in_transaction() is False


@pytest.mark.asyncio
async def test_default_session_delegates_rollback_and_close() -> None:
    underlying = RecordingSession()
    session = EngineSession(underlying)

    await session.begin()
    await session.delete("item")
    await session.rollback()
    await session.close()

    assert underlying.events == ["begin", ("delete", "item"), "rollback", "close"]


@pytest.mark.asyncio
async def test_default_session_enforces_read_only_spec_before_mutation() -> None:
    session = EngineSession(RecordingSession(), EngineSessionSpec(read_only=True))

    with pytest.raises(RuntimeError, match="read-only"):
        session.add("item")
    with pytest.raises(RuntimeError, match="read-only"):
        await session.delete("item")


def test_wrap_sessionmaker_returns_isolated_default_sessions_with_spec() -> None:
    made: list[RecordingSession] = []

    def maker() -> RecordingSession:
        session = RecordingSession()
        made.append(session)
        return session

    spec = EngineSessionSpec(read_only=True, tag="tenant-a")
    wrapped = wrap_sessionmaker(maker, spec)
    first = wrapped()
    second = wrapped()

    assert isinstance(first, EngineSession)
    assert isinstance(second, EngineSession)
    assert first is not second
    assert first._u is made[0]
    assert second._u is made[1]
    assert isinstance(first, EngineSessionBase)
    assert isinstance(first, EngineSessionSpec)
    assert first.read_only is True
    assert first.tag == "tenant-a"
    assert isinstance(second, EngineSessionBase)
    assert isinstance(second, EngineSessionSpec)
    assert second.read_only is True
    assert second.tag == "tenant-a"
