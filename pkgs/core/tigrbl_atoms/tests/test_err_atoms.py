from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms import events as _ev
from tigrbl_atoms.atoms.err import REGISTRY, classify, ctx_build, rollback, transport_shape


def test_err_rollback_anchor_constant() -> None:
    assert rollback.ANCHOR == _ev.ERR_ROLLBACK


def test_err_registry_includes_typed_error_atoms() -> None:
    assert REGISTRY[("err", "ctx_build")] == (ctx_build.ANCHOR, ctx_build.run)
    assert REGISTRY[("err", "classify")] == (classify.ANCHOR, classify.run)
    assert REGISTRY[("err", "rollback")] == (rollback.ANCHOR, rollback.run)
    assert REGISTRY[("err", "transport_shape")] == (
        transport_shape.ANCHOR,
        transport_shape.run,
    )


def test_resolve_db_handle_prefers_db_over_session() -> None:
    db = object()
    session = object()
    ctx = SimpleNamespace(db=db, session=session)

    out = rollback._resolve_db_handle(ctx)

    assert out is db


def test_run_calls_sync_rollback_and_release_hook() -> None:
    called: list[str] = []

    class Db:
        def rollback(self) -> None:
            called.append("rollback")

    def release() -> None:
        called.append("release")

    ctx = SimpleNamespace(db=Db(), temp={"__sys_db_release__": release})

    asyncio.run(rollback.run(None, ctx))

    assert called == ["rollback", "release"]
    assert "__sys_db_release__" not in ctx.temp


def test_run_awaits_async_rollback() -> None:
    called: list[str] = []

    class Db:
        async def rollback(self) -> None:
            called.append("rollback")

    ctx = SimpleNamespace(db=Db(), temp={})

    asyncio.run(rollback.run(None, ctx))

    assert called == ["rollback"]


def test_run_uses_session_when_db_missing() -> None:
    called: list[str] = []

    class Session:
        def rollback(self) -> None:
            called.append("rollback")

    ctx = SimpleNamespace(session=Session(), temp={})

    asyncio.run(rollback.run(None, ctx))

    assert called == ["rollback"]


def test_run_noops_when_no_db_or_session_present() -> None:
    ctx = SimpleNamespace(temp={})

    asyncio.run(rollback.run(None, ctx))

    assert ctx.temp == {}
