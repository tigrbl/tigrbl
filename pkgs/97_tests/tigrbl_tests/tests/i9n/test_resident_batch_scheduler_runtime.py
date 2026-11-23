from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import admit, await_seal
from tigrbl_atoms.atoms.batch.scheduler import ResidentBatchScheduler
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture
from tigrbl_runtime.executors.packed import PackedPlanExecutor


class Ctx(SimpleNamespace):
    def promote(self, _stage):
        return self


class Db:
    def __init__(self) -> None:
        self.calls = []

    async def executemany(self, statement, parameter_sets):
        self.calls.append((statement, list(parameter_sets)))
        return [{"id": item["id"]} for item in parameter_sets]


class Hot:
    batch = {
        "enabled": True,
        "max_size": 2,
        "max_delay_ms": 60_000,
        "max_queue_depth": 8,
    }


def _ctx(db: Db, scheduler: ResidentBatchScheduler, item_id: int) -> Ctx:
    ctx = Ctx(
        db=db,
        op="create",
        model=object,
        payload_ref={"id": item_id},
        transport_sink_index=item_id - 1,
        transport_sink_family="jsonrpc",
        correlation_id=f"rpc-{item_id}",
        temp={},
    )
    PackedPlanExecutor._seed_batch_policy_from_hot_plan(ctx, Hot())
    ctx.batch_scheduler = scheduler
    ctx.temp["batch_scheduler"] = scheduler
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)
    ctx.temp["intent"]["statement"] = "insert"
    final_group_key._run(None, ctx)
    return ctx


@pytest.mark.asyncio
async def test_runtime_admission_atoms_use_resident_scheduler_across_contexts() -> None:
    db = Db()
    scheduler = ResidentBatchScheduler()
    ctx1 = _ctx(db, scheduler, 1)
    ctx2 = _ctx(db, scheduler, 2)

    async def run_admission(ctx: Ctx):
        await admit.INSTANCE(None, ctx)
        await await_seal.INSTANCE(None, ctx)
        return ctx.result

    results = await asyncio.gather(run_admission(ctx1), run_admission(ctx2))

    assert results == [{"id": 1}, {"id": 2}]
    assert db.calls == [("insert", [{"id": 1}, {"id": 2}])]
    assert ctx1.temp["batch_resident_handled"] is True
    assert ctx2.temp["batch_resident_handled"] is True
    assert ctx1.temp["batch_group"] is ctx2.temp["batch_group"]


@pytest.mark.asyncio
async def test_shared_sqlite_batch_links_new_transaction_after_rollback() -> None:
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError
    from tigrbl_engine_sqlite.engine import sqlite_engine

    engine, maker = sqlite_engine()
    session = maker()
    scheduler = ResidentBatchScheduler()
    try:
        await session.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY)"))
        await session.commit()

        async def attempt(ids, revision):
            contexts = [_ctx(session, scheduler, n) for n in (1, 2)]
            statement = text("INSERT INTO items VALUES (:id)")
            for n, (ctx, value) in enumerate(zip(contexts, ids)):
                intent = ctx.temp["intent"]
                intent["statement"] = statement
                intent["payload_ref"] = {"id": value}
                intent["identity"] = {
                    "correlation_id": f"request-{n}", "invocation_id": f"invocation-{n}",
                    "attempt_id": f"attempt-{revision}-{n}",
                }
                ctx.temp["batch_db_acquire"] = lambda _ctx: session
                ctx.payload_ref = {"id": value}

            async def run(ctx):
                await admit.INSTANCE(None, ctx)
                await await_seal.INSTANCE(None, ctx)

            results = await asyncio.gather(*(run(ctx) for ctx in contexts), return_exceptions=True)
            return contexts, results

        failed, errors = await attempt((3, 3), 1)
        assert all(isinstance(error, IntegrityError) for error in errors), errors
        retried, results = await attempt((3, 4), 2)
        assert results == [None, None]
        first, second = [
            [ctx.temp["transaction_participation"][0] for ctx in cohort]
            for cohort in (failed, retried)
        ]
        assert {link["transaction_id"] for link in first}.isdisjoint(
            {link["transaction_id"] for link in second}
        )
        assert [link["invocation_id"] for link in first] == [link["invocation_id"] for link in second]
        for cohort, outcome in ((failed, "rolled_back"), (retried, "committed")):
            lifecycle = cohort[0].temp["transaction_events"]
            assert lifecycle == cohort[1].temp["transaction_events"]
            assert [event["outcome"] for event in lifecycle] == ["begin", outcome]
    finally:
        await session.close()
        engine.dispose()
