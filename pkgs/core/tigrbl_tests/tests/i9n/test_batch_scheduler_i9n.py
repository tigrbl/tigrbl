from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import admit, await_seal, execute, result_slots, seal_check
from tigrbl_atoms.atoms.batch import prepare_execute
from tigrbl_atoms.atoms.fanout import emit_many, shape
from tigrbl_atoms.atoms.intent import build as intent_build
from tigrbl_atoms.atoms.intent import final_group_key
from tigrbl_atoms.atoms.transport import sink_bind, unit_capture


class Db:
    def __init__(self) -> None:
        self.calls = []

    async def executemany(self, stmt, parameter_sets):
        self.calls.append((stmt, list(parameter_sets)))
        return [{"ok": item["id"]} for item in parameter_sets]


class Sink:
    def __init__(self) -> None:
        self.batches = []

    async def emit_many(self, payloads):
        self.batches.append(list(payloads))


def _admit_one(ctx, *, item_id: int, sink: Sink) -> None:
    ctx.payload_ref = {"id": item_id}
    ctx.correlation_id = f"c{item_id}"
    ctx.transport_sink = sink
    ctx.transport_sink_index = item_id - 1
    ctx.transport_sink_family = "i9n"
    unit_capture._run(None, ctx)
    sink_bind._run(None, ctx)
    intent_build._run(None, ctx)
    ctx.temp["intent"]["statement"] = "insert"
    ctx.temp["intent"]["force_seal"] = item_id == 2
    final_group_key._run(None, ctx)
    admit._run(None, ctx)
    seal_check._run(None, ctx)
    await_seal._run(None, ctx)


@pytest.mark.asyncio
async def test_batch_scheduler_i9n_executemany_to_grouped_fanout() -> None:
    sink = Sink()
    ctx = SimpleNamespace(
        db=Db(),
        op="create",
        model=object,
        batch_policy={"enabled": True, "max_size": 2},
        temp={},
    )

    _admit_one(ctx, item_id=1, sink=sink)
    assert ctx.temp.get("batch_group") is None
    _admit_one(ctx, item_id=2, sink=sink)
    group = ctx.temp["batch_group"]

    prepare_execute._run(None, ctx)
    await execute._run(None, ctx)
    result_slots._run(None, ctx)

    fanout_payloads = []
    for admission in group.admissions:
        ctx.temp["batch_admission"] = admission
        shape._run(None, ctx)
        fanout_payloads.append((admission, ctx.temp["fanout_payload"]))
    ctx.temp["fanout_payloads"] = fanout_payloads
    await emit_many._run(None, ctx)

    assert ctx.db.calls == [("insert", [{"id": 1}, {"id": 2}])]
    assert group.result_slots == [{"ok": 1}, {"ok": 2}]
    assert sink.batches == [
        [
            {"admission_id": group.admissions[0].admission_id, "correlation_id": "c1", "result": {"ok": 1}},
            {"admission_id": group.admissions[1].admission_id, "correlation_id": "c2", "result": {"ok": 2}},
        ]
    ]


@pytest.mark.asyncio
async def test_batch_scheduler_i9n_marks_scalar_fallback_for_unsupported_session() -> None:
    sink = Sink()
    ctx = SimpleNamespace(
        db=object(),
        op="create",
        model=object,
        batch_policy={
            "enabled": True,
            "max_size": 1,
            "conflict_policy": "single_fallback",
        },
        temp={},
    )

    _admit_one(ctx, item_id=1, sink=sink)
    prepare_execute._run(None, ctx)
    await execute._run(None, ctx)
    result_slots._run(None, ctx)

    assert ctx.temp["batch_execution_kind"] == "scalar_fallback"
    assert ctx.temp["batch_fallback_reason"] == "unsupported_executemany"
    assert ctx.temp["batch_group"].result_slots == [None]
