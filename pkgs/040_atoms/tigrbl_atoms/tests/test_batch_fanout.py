from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import error_project, result_slots
from tigrbl_atoms.atoms.batch._types import BatchAdmission, BatchGroup
from tigrbl_atoms.atoms.fanout import emit_many, shape


class Sink:
    def __init__(self) -> None:
        self.items: list[object] = []
        self.batches: list[list[object]] = []

    async def emit(self, item):
        self.items.append(item)

    async def emit_many(self, items):
        self.batches.append(list(items))


def _group_with_admissions(sink: object | None = None) -> BatchGroup:
    group = BatchGroup(group_key=("engine", "tenant", "create"))
    for idx in range(2):
        group.admissions.append(
            BatchAdmission(
                admission_id=idx + 1,
                group_key=group.group_key,
                intent={"correlation_id": f"c{idx + 1}"},
                sink=sink,
                sink_index=idx,
                result_index=idx,
            )
        )
    return group


def test_result_slots_pad_to_admission_count_for_scalar_fallback() -> None:
    group = _group_with_admissions()
    ctx = SimpleNamespace(
        temp={
            "batch_group": group,
            "batch_execution_kind": "scalar_fallback",
        }
    )

    result_slots._run(None, ctx)

    assert group.result_slots == [None, None]


def test_shape_projects_only_the_current_admission_slot() -> None:
    group = _group_with_admissions()
    group.result_slots = ["first", "second"]
    ctx = SimpleNamespace(
        temp={"batch_group": group, "batch_admission": group.admissions[1]}
    )

    shape._run(None, ctx)

    assert ctx.result == "second"
    assert ctx.temp["fanout_payload"] == {
        "admission_id": 2,
        "correlation_id": "c2",
        "result": "second",
    }


def test_error_project_writes_current_admission_error_slot() -> None:
    group = _group_with_admissions()
    ctx = SimpleNamespace(
        error=ValueError("bad"),
        temp={"batch_group": group, "batch_admission": group.admissions[0]},
    )

    error_project._run(None, ctx)

    assert isinstance(group.error_slots[0], ValueError)
    assert ctx.result["admission_id"] == 1


@pytest.mark.asyncio
async def test_emit_many_groups_payloads_by_sink() -> None:
    sink = Sink()
    group = _group_with_admissions(sink)
    ctx = SimpleNamespace(
        temp={
            "batch_group": group,
            "fanout_payloads": [
                (group.admissions[0], {"admission_id": 1}),
                (group.admissions[1], {"admission_id": 2}),
            ],
        }
    )

    await emit_many._run(None, ctx)

    assert sink.batches == [[{"admission_id": 1}, {"admission_id": 2}]]
