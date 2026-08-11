from __future__ import annotations

import inspect

import pytest
from tigrbl_base._base import EngineSessionBase
from tigrbl_core._spec import EngineSessionSpec

from tigrbl_engine_memdedupe.dedupe import DedupeSet
from tigrbl_engine_memdedupe.engine import DedupeEngine
from tigrbl_engine_memdedupe.session import AsyncDedupeSession, DedupeSession


def make_session(
    session_type: type[DedupeSession] = DedupeSession,
    *,
    spec: EngineSessionSpec | None = None,
) -> DedupeSession:
    return session_type(DedupeEngine(DedupeSet()), spec=spec)


@pytest.mark.asyncio
@pytest.mark.parametrize("session_type", [DedupeSession, AsyncDedupeSession])
async def test_delete_and_close_follow_session_base_contract(
    session_type: type[DedupeSession],
) -> None:
    session = make_session(session_type)
    session.mark("order-42")

    assert isinstance(session, EngineSessionBase)
    assert inspect.iscoroutinefunction(session.delete)
    assert await session.delete("order-42") is None
    assert session.seen("order-42") is False

    assert inspect.iscoroutinefunction(session.close)
    await session.close()
    with pytest.raises(RuntimeError, match="session is closed"):
        session.seen("order-42")


@pytest.mark.asyncio
async def test_forget_reports_whether_key_was_removed() -> None:
    session = make_session()
    session.mark("order-42")

    assert await session.forget("order-42") is True
    assert await session.forget("order-42") is False


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["mark", "mark_if_absent", "forget", "reset"])
async def test_all_mutations_enforce_read_only_session_spec(operation: str) -> None:
    session = make_session(spec=EngineSessionSpec(read_only=True))

    with pytest.raises(RuntimeError, match="read-only engine session"):
        result = getattr(session, operation)("order-42") if operation != "reset" else session.reset()
        if inspect.isawaitable(result):
            await result


@pytest.mark.asyncio
async def test_generic_orm_and_statement_surfaces_fail_actionably() -> None:
    session = make_session()

    with pytest.raises(TypeError, match=r"use mark\(\)"):
        session.add(object())
    with pytest.raises(TypeError, match=r"use seen\(\)"):
        await session.get(object, "order-42")
    with pytest.raises(TypeError, match="do not execute statements"):
        await session.execute("statement")
    with pytest.raises(TypeError, match="statement batches"):
        await session.executeloop(["statement"])
    with pytest.raises(TypeError, match="statement batches"):
        await session.executemany("statement", [{}])

    await session.flush()
    await session.refresh(object())


@pytest.mark.asyncio
async def test_keys_must_be_strings() -> None:
    session = make_session()

    with pytest.raises(TypeError, match="keys must be strings"):
        session.seen(42)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="keys must be strings"):
        await session.delete(42)
