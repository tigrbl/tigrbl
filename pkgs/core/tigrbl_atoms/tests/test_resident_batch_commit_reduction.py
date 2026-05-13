from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from tigrbl_atoms.atoms.batch.scheduler import ResidentBatchScheduler
from tigrbl_atoms.atoms.sys import commit_tx, handler_create, handler_persistence, start_tx


class BatchSession:
    def __init__(self, parent: "SessionProvider") -> None:
        self.parent = parent
        self.begin_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.executemany_calls: list[tuple[str, list[dict[str, int]]]] = []

    async def begin(self) -> None:
        self.begin_count += 1
        self.parent.begin_count += 1

    async def executemany(self, statement: str, parameter_sets):
        rows = list(parameter_sets)
        self.executemany_calls.append((statement, rows))
        self.parent.executemany_batch_sizes.append(len(rows))
        return [{"id": row["id"]} for row in rows]

    async def commit(self) -> None:
        self.commit_count += 1
        self.parent.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_count += 1
        self.parent.rollback_count += 1

    async def close(self) -> None:
        self.parent.close_count += 1


class SessionProvider:
    def __init__(self) -> None:
        self.sessions: list[BatchSession] = []
        self.begin_count = 0
        self.commit_count = 0
        self.rollback_count = 0
        self.close_count = 0
        self.executemany_batch_sizes: list[int] = []

    def acquire(self, _ctx):
        session = BatchSession(self)
        self.sessions.append(session)
        return session, session.close


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "resident_batch_widgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class SqlAlchemyProvider:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.commit_count = 0
        self.close_count = 0

    def acquire(self, _ctx):
        session = Session(self.engine, expire_on_commit=False)

        def release() -> None:
            session.close()
            self.close_count += 1

        original_commit = session.commit

        def commit() -> None:
            self.commit_count += 1
            original_commit()

        session.commit = commit  # type: ignore[method-assign]
        return session, release


def _ctx(provider: SessionProvider, item_id: int) -> SimpleNamespace:
    return SimpleNamespace(
        batch_policy={"enabled": True, "max_size": 25, "max_delay_ms": 1000},
        batch_db_acquire=provider.acquire,
        temp={
            "intent": {
                "final_group_key": ("sqlite", "tenant", "create"),
                "op": "create",
                "payload_ref": {"id": item_id},
                "statement": "insert",
            },
            "transport": {
                "sink_index": item_id,
                "correlation_id": f"c{item_id}",
            },
        },
    )


def _create_ctx(provider: SqlAlchemyProvider, item_id: int) -> SimpleNamespace:
    return SimpleNamespace(
        batch_policy={"enabled": True, "max_size": 25, "max_delay_ms": 1000},
        batch_db_acquire=provider.acquire,
        temp={
            "intent": {
                "final_group_key": ("sqlite", "tenant", "create", Widget),
                "op": "create",
                "target": "create",
                "model": Widget,
                "payload_ref": {"id": item_id, "name": f"w{item_id}"},
            },
            "transport": {
                "sink_index": item_id,
                "correlation_id": f"c{item_id}",
            },
        },
    )


@pytest.mark.asyncio
async def test_resident_scheduler_reduces_250_admissions_to_10_commits() -> None:
    provider = SessionProvider()
    scheduler = ResidentBatchScheduler()
    contexts = [_ctx(provider, item_id) for item_id in range(250)]

    async def admit_and_wait(ctx):
        await scheduler.admit(ctx)
        return await scheduler.await_result(ctx)

    results = await asyncio.gather(*(admit_and_wait(ctx) for ctx in contexts))

    assert len(results) == 250
    assert provider.executemany_batch_sizes == [25] * 10
    assert provider.begin_count == 10
    assert provider.commit_count == 10
    assert provider.rollback_count == 0
    assert provider.close_count == 10
    assert scheduler.metrics["commits"] == 10
    assert scheduler.metrics["executemany"] == 10


@pytest.mark.asyncio
async def test_resident_create_group_uses_insert_executemany_not_bulk_create() -> None:
    provider = SqlAlchemyProvider()
    scheduler = ResidentBatchScheduler()
    contexts = [_create_ctx(provider, item_id) for item_id in range(50)]

    async def admit_and_wait(ctx):
        await scheduler.admit(ctx)
        return await scheduler.await_result(ctx)

    results = await asyncio.gather(*(admit_and_wait(ctx) for ctx in contexts))

    with Session(provider.engine) as session:
        names = session.scalars(select(Widget.name).order_by(Widget.id)).all()

    assert [result.name for result in results] == [f"w{item_id}" for item_id in range(50)]
    assert names == [f"w{item_id}" for item_id in range(50)]
    assert provider.commit_count == 2
    assert provider.close_count == 2
    assert scheduler.metrics["commits"] == 2
    assert scheduler.metrics["executemany"] == 2
    assert scheduler.metrics["fallback"] == 0


@pytest.mark.asyncio
async def test_request_local_tx_and_handlers_skip_resident_batch_context() -> None:
    calls: list[str] = []

    class Db:
        async def begin(self) -> None:
            calls.append("begin")

        async def commit(self) -> None:
            calls.append("commit")

        def in_transaction(self) -> bool:
            return True

    ctx = SimpleNamespace(
        db=Db(),
        model=object,
        payload={},
        temp={"batch_resident_admitted": True},
    )

    await start_tx._run(None, ctx)
    await handler_create._run(object, ctx)
    await handler_persistence._run(object, ctx)
    await commit_tx._run(None, ctx)

    assert calls == []
    assert ctx.temp["__sys_tx_open__"] is False
