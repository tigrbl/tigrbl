from __future__ import annotations

from types import SimpleNamespace

from tigrbl_atoms.atoms.batch import prepare_execute
from tigrbl_atoms.atoms.batch._types import BatchAdmission, BatchGroup


def _admission(
    admission_id: int,
    *,
    statement: object = "insert",
    payload: object | None = None,
) -> BatchAdmission:
    return BatchAdmission(
        admission_id=admission_id,
        group_key=("engine", "tenant", "create"),
        intent={
            "statement": statement,
            "payload_ref": payload if payload is not None else {"id": admission_id},
        },
        sink=None,
        sink_index=0,
        result_index=admission_id - 1,
    )


def test_prepare_execute_builds_executemany_payload_for_common_statement() -> None:
    group = BatchGroup(group_key=("engine", "tenant", "create"))
    group.admissions.extend([_admission(1), _admission(2)])
    ctx = SimpleNamespace(temp={"batch_group": group})

    prepare_execute._run(None, ctx)

    assert ctx.temp["batch_execution_kind"] == "executemany"
    assert ctx.temp["batch_statement"] == "insert"
    assert ctx.temp["batch_parameter_sets"] == [{"id": 1}, {"id": 2}]


def test_prepare_execute_builds_executeloop_payload_for_mixed_statements() -> None:
    group = BatchGroup(group_key=("engine", "tenant", "custom"))
    group.admissions.extend(
        [
            _admission(1, statement="select-one", payload={"id": 1}),
            _admission(2, statement="select-two", payload={"id": 2}),
        ]
    )
    ctx = SimpleNamespace(temp={"batch_group": group})

    prepare_execute._run(None, ctx)

    assert ctx.temp["batch_execution_kind"] == "executeloop"
    assert ctx.temp["batch_statements"] == [
        ("select-one", {"id": 1}),
        ("select-two", {"id": 2}),
    ]


def test_prepare_execute_marks_unsupported_without_statement() -> None:
    group = BatchGroup(group_key=("engine", "tenant", "create"))
    admission = _admission(1)
    admission.intent.pop("statement")
    group.admissions.append(admission)
    ctx = SimpleNamespace(temp={"batch_group": group})

    prepare_execute._run(None, ctx)

    assert ctx.temp["batch_execution_kind"] == "unsupported"
    assert ctx.temp["batch_unsupported_reason"] == "missing_statement"
