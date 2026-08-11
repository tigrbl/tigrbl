from __future__ import annotations

import inspect

import pytest
from tigrbl_core._spec import EngineSessionSpec

from tigrbl_engine_memdedupe.dedupe import DedupeSet
from tigrbl_engine_memdedupe.session import AsyncDedupeSession, DedupeSession


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [DedupeSession, AsyncDedupeSession])
async def test_delete_and_close_are_async(session_type: type[DedupeSession]) -> None:
    session = session_type(DedupeSet())
    session.mark("order-42")

    assert inspect.iscoroutinefunction(session.delete)
    assert await session.delete("order-42") is True
    assert await session.delete("order-42") is False
    assert session._dirty is True

    assert inspect.iscoroutinefunction(session.close)
    await session.close()
    with pytest.raises(RuntimeError, match="session is closed"):
        session.seen("order-42")


@pytest.mark.asyncio
async def test_delete_enforces_read_only_session_spec() -> None:
    session = DedupeSession(DedupeSet())
    session.apply_spec(EngineSessionSpec(read_only=True))
    session.mark("order-42")

    with pytest.raises(RuntimeError, match="read-only engine session"):
        await session.delete("order-42")


@pytest.mark.asyncio
async def test_general_crud_and_execution_hooks_remain_unsupported() -> None:
    session = DedupeSession(DedupeSet())

    with pytest.raises(NotImplementedError):
        session.add(object())
    with pytest.raises(NotImplementedError):
        await session.get(object, "order-42")
    with pytest.raises(NotImplementedError):
        await session.execute("statement")
    with pytest.raises(NotImplementedError):
        await session.executeloop(["statement"])
    with pytest.raises(NotImplementedError):
        await session.executemany("statement", [{}])

    await session.flush()
    await session.refresh(object())
