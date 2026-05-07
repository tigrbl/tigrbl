from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Executing
from ...types import Atom, Ctx, ExecutingCtx
from ..hot.slots import HotSlotPayload

ANCHOR = _ev.BATCH_PREPARE_EXECUTE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    if ctx.temp.get("batch_resident_handled"):
        return
    group = ctx.temp.get("batch_group")
    if group is None:
        return
    if ctx.temp.get("batch_execution_kind") == "scalar_fallback":
        group.fallback = True
        group.fallback_reason = str(ctx.temp.get("batch_fallback_reason") or "")
        return

    explicit_stmt = ctx.temp.get("batch_statement", getattr(ctx, "batch_statement", None))
    explicit_statements = ctx.temp.get(
        "batch_statements", getattr(ctx, "batch_statements", None)
    )
    parameter_sets = [_payload_for_execute(admission) for admission in group.admissions]
    if explicit_stmt is not None:
        ctx.temp["batch_execution_kind"] = "executemany"
        ctx.temp["batch_statement"] = explicit_stmt
        ctx.temp["batch_parameter_sets"] = parameter_sets
        _prepare_slot_rows(group, parameter_sets)
        return
    if explicit_statements is not None:
        ctx.temp["batch_execution_kind"] = "executeloop"
        ctx.temp["batch_statements"] = explicit_statements
        return

    statements = [admission.intent.get("statement") for admission in group.admissions]
    if any(statement is None for statement in statements):
        ctx.temp["batch_execution_kind"] = "unsupported"
        ctx.temp["batch_unsupported_reason"] = "missing_statement"
        return

    first = statements[0] if statements else None
    if statements and all(statement == first for statement in statements):
        ctx.temp["batch_execution_kind"] = "executemany"
        ctx.temp["batch_statement"] = first
        ctx.temp["batch_parameter_sets"] = parameter_sets
        _prepare_slot_rows(group, parameter_sets)
        return

    ctx.temp["batch_execution_kind"] = "executeloop"
    ctx.temp["batch_statements"] = list(zip(statements, parameter_sets))


def _payload_for_execute(admission: Any) -> Any:
    slot_payload = getattr(admission, "slot_payload", None)
    if isinstance(slot_payload, HotSlotPayload):
        return slot_payload.as_mapping()
    return admission.intent.get("payload_ref")


def _prepare_slot_rows(group: Any, parameter_sets: list[Any]) -> None:
    slot_payloads = [
        getattr(admission, "slot_payload", None) for admission in group.admissions
    ]
    if not slot_payloads or not all(isinstance(item, HotSlotPayload) for item in slot_payloads):
        return
    first = slot_payloads[0]
    columns = first.field_names
    group.parameter_columns = columns
    rows = []
    for admission, payload in zip(group.admissions, slot_payloads, strict=False):
        row = payload.row_tuple(columns)
        admission.parameter_row = row
        rows.append(row)
    group.parameter_rows = rows
    parameter_sets[:] = rows


hot_run = _run


class AtomImpl(Atom[Executing, Executing, Exception]):
    name = "batch.prepare_execute"
    anchor = ANCHOR

    async def __call__(
        self, obj: object | None, ctx: Ctx[Executing]
    ) -> Ctx[Executing]:
        _run(obj, ctx)
        return ctx.promote(ExecutingCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
