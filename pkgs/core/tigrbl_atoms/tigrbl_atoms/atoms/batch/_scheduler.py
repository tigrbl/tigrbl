from __future__ import annotations

from itertools import count
from time import monotonic_ns
from typing import Any, Mapping

from .._temp import _ensure_temp
from ._types import BatchAdmission, BatchGroup

_next_admission_id = count(1)


def enabled(ctx: Any) -> bool:
    policy = getattr(ctx, "batch_policy", None)
    if isinstance(policy, Mapping) and bool(policy.get("enabled")):
        return True
    temp = _ensure_temp(ctx)
    temp_policy = temp.get("batch_policy")
    return bool(getattr(ctx, "batch_enabled", False)) or (
        isinstance(temp_policy, Mapping) and bool(temp_policy.get("enabled"))
    )


def _batch_state(ctx: Any) -> dict[str, Any]:
    temp = _ensure_temp(ctx)
    return temp.setdefault(
        "batch",
        {
            "open": {},
            "sealed": None,
            "admission": None,
            "metrics": {},
        },
    )


def admit(ctx: Any) -> BatchAdmission:
    if not enabled(ctx):
        raise RuntimeError("batch admission requested while batching is disabled")
    state = _batch_state(ctx)
    intent = ctx.temp["intent"]
    transport = ctx.temp.get("transport", {})
    group_key = intent["final_group_key"]
    group = state["open"].setdefault(group_key, BatchGroup(group_key=group_key))
    admission = BatchAdmission(
        admission_id=next(_next_admission_id),
        group_key=group_key,
        intent=intent,
        sink=transport.get("sink"),
        sink_index=int(transport.get("sink_index", 0) or 0),
    )
    admission.result_index = len(group.admissions)
    group.admissions.append(admission)
    state["admission"] = admission
    ctx.temp["batch_admission"] = admission
    return admission


def dedupe(ctx: Any) -> None:
    admission = ctx.temp.get("batch_admission")
    if admission is None:
        return
    dedupe_key = admission.intent.get("dedupe_key")
    if dedupe_key is None:
        return
    state = _batch_state(ctx)
    seen = state.setdefault("dedupe", {})
    previous = seen.setdefault(dedupe_key, admission)
    ctx.temp["batch_admission"] = previous


def seal_check(ctx: Any) -> bool:
    state = _batch_state(ctx)
    admission = state.get("admission")
    if admission is None:
        return False
    group = state["open"][admission.group_key]
    policy = admission.intent.get("batch_policy", {})
    max_count = int(policy.get("max_count", 64))
    max_delay_ns = int(policy.get("max_delay_ns", 1_000_000))
    age_ns = monotonic_ns() - group.created_ns
    should_seal = (
        len(group.admissions) >= max_count
        or age_ns >= max_delay_ns
        or bool(admission.intent.get("force_seal"))
    )
    if should_seal:
        group.sealed = True
        state["sealed"] = group
        state["open"].pop(group.group_key, None)
    return should_seal


def await_seal(ctx: Any) -> BatchGroup | None:
    return _batch_state(ctx).get("sealed")


def cleanup(ctx: Any) -> None:
    state = ctx.temp.get("batch")
    if not isinstance(state, dict):
        return
    state.pop("admission", None)
    state.pop("sealed", None)
