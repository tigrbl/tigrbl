from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch.scheduler import ResidentBatchScheduler


class Db:
    def __init__(self) -> None:
        self.executemany_calls = []

    async def executemany(self, statement, parameter_sets):
        self.executemany_calls.append((statement, list(parameter_sets)))
        return [{"ok": item["id"]} for item in parameter_sets]


def _ctx(db: Db, item_id: int, *, max_size: int = 2) -> SimpleNamespace:
    return SimpleNamespace(
        db=db,
        batch_policy={"enabled": True, "max_size": max_size, "max_delay_ms": 1},
        temp={
            "intent": {
                "final_group_key": ("sqlite", "tenant", "create"),
                "op": "create",
                "payload_ref": {"id": item_id},
                "statement": "insert",
            },
            "transport": {
                "sink_index": item_id - 1,
                "correlation_id": f"c{item_id}",
            },
        },
    )


@pytest.mark.asyncio
async def test_resident_scheduler_seals_by_size_and_executes_once() -> None:
    db = Db()
    scheduler = ResidentBatchScheduler()
    ctx1 = _ctx(db, 1)
    ctx2 = _ctx(db, 2)

    async def admit_and_wait(ctx):
        await scheduler.admit(ctx)
        return await scheduler.await_result(ctx)

    results = await asyncio.gather(admit_and_wait(ctx1), admit_and_wait(ctx2))

    assert results == [{"ok": 1}, {"ok": 2}]
    assert db.executemany_calls == [("insert", [{"id": 1}, {"id": 2}])]
    assert ctx1.result == {"ok": 1}
    assert ctx2.result == {"ok": 2}
    assert ctx1.temp["batch_group"] is ctx2.temp["batch_group"]
    assert scheduler.metrics["sealed"] == 1
    assert scheduler.metrics["executemany"] == 1


@pytest.mark.asyncio
async def test_resident_scheduler_seals_by_timer() -> None:
    db = Db()
    scheduler = ResidentBatchScheduler()
    ctx = _ctx(db, 1, max_size=10)

    await scheduler.admit(ctx)
    result = await scheduler.await_result(ctx)

    assert result == {"ok": 1}
    assert db.executemany_calls == [("insert", [{"id": 1}])]
    assert ctx.temp["batch_group"].sealed is True
