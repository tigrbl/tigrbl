from __future__ import annotations

import inspect
from types import SimpleNamespace

import pytest

from tigrbl_concrete._concrete import engine_resolver
from tigrbl_concrete.ddl import initialize


class _Table:
    pass


class _SyncSession:
    closed = False

    def get_bind(self):
        return self

    def close(self) -> None:
        self.closed = True


class _AsyncMemorySession:
    closed = False

    async def run_sync(self, _fn):
        raise AssertionError("non-SQL memory sessions must not enter SQL DDL")

    async def close(self) -> None:
        self.closed = True


class _SyncProvider:
    def __init__(self) -> None:
        self.session = _SyncSession()

    def get_db(self):
        try:
            yield self.session
        finally:
            self.session.close()


class _AsyncProvider:
    def __init__(self) -> None:
        self.session = _AsyncMemorySession()

    async def get_db(self):
        try:
            yield self.session
        finally:
            await self.session.close()


@pytest.mark.asyncio
async def test_initialize_dispatches_each_mixed_provider_by_its_own_session_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sync_provider = _SyncProvider()
    async_provider = _AsyncProvider()
    sync_model = SimpleNamespace(__table__=_Table())
    async_model = SimpleNamespace(__table__=_Table())
    app = SimpleNamespace(tables={"sync": sync_model, "memory": async_model})
    ready: list[object] = []

    def resolve_provider(**kwargs):
        model = kwargs.get("model")
        if model is async_model:
            return async_provider
        return sync_provider

    monkeypatch.setattr(engine_resolver, "resolve_provider", resolve_provider)
    monkeypatch.setattr(engine_resolver, "mark_schema_ready", ready.append)

    result = initialize(app)

    assert inspect.isawaitable(result)
    await result
    assert ready == [sync_provider, async_provider]
    assert sync_provider.session.closed is True
    assert async_provider.session.closed is True
    assert app._ddl_executed is True
