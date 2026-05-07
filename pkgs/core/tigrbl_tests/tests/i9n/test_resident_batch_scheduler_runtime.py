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
        "max_delay_ms": 1,
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
