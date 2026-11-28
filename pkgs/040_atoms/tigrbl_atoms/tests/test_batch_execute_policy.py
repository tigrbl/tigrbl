from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.batch import execute
from tigrbl_atoms.atoms.batch._types import BatchGroup


@pytest.mark.asyncio
async def test_execute_uses_executemany_for_prepared_many_payload() -> None:
    class Db:
        async def executemany(self, stmt, parameter_sets):
            return [{"stmt": stmt, "params": item} for item in parameter_sets]

    group = BatchGroup(group_key=("engine", "tenant", "create"))
    ctx = SimpleNamespace(
        db=Db(),
        batch_policy={"enabled": True},
        temp={
            "batch_group": group,
            "batch_execution_kind": "executemany",
            "batch_statement": "insert",
            "batch_parameter_sets": [{"id": 1}, {"id": 2}],
        },
    )

    await execute._run(None, ctx)

    assert ctx.temp["batch_raw_results"] == [
        {"stmt": "insert", "params": {"id": 1}},
        {"stmt": "insert", "params": {"id": 2}},
    ]


@pytest.mark.asyncio
async def test_execute_uses_executeloop_for_prepared_loop_payload() -> None:
    class Db:
        def executeloop(self, statements):
            return [("loop", statement) for statement in statements]

    ctx = SimpleNamespace(
        db=Db(),
        batch_policy={"enabled": True},
        temp={
            "batch_group": BatchGroup(group_key=("engine", "tenant", "custom")),
            "batch_execution_kind": "executeloop",
            "batch_statements": [("select", {"id": 1})],
        },
    )

    await execute._run(None, ctx)

    assert ctx.temp["batch_raw_results"] == [("loop", ("select", {"id": 1}))]


@pytest.mark.asyncio
async def test_execute_marks_scalar_fallback_when_session_is_unsupported() -> None:
    ctx = SimpleNamespace(
        db=object(),
        batch_policy={"enabled": True, "conflict_policy": "single_fallback"},
        temp={
            "batch_group": BatchGroup(group_key=("engine", "tenant", "create")),
            "batch_execution_kind": "executemany",
            "batch_statement": "insert",
            "batch_parameter_sets": [{"id": 1}],
        },
    )

    await execute._run(None, ctx)

    assert ctx.temp["batch_execution_kind"] == "scalar_fallback"
    assert ctx.temp["batch_fallback_reason"] == "unsupported_executemany"


@pytest.mark.asyncio
async def test_execute_rejects_when_policy_disallows_fallback() -> None:
    ctx = SimpleNamespace(
        db=object(),
        batch_policy={"enabled": True, "conflict_policy": "reject"},
        temp={
            "batch_group": BatchGroup(group_key=("engine", "tenant", "create")),
            "batch_execution_kind": "executemany",
            "batch_statement": "insert",
            "batch_parameter_sets": [{"id": 1}],
        },
    )

    with pytest.raises(NotImplementedError, match="unsupported_executemany"):
        await execute._run(None, ctx)
