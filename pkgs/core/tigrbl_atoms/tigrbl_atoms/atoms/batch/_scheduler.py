from __future__ import annotations

from itertools import count
from time import monotonic_ns
from typing import Any, Mapping

from .._temp import _ensure_temp
from ._types import BatchAdmission, BatchGroup, BatchPolicy

_next_admission_id = count(1)


def enabled(ctx: Any) -> bool:
    return policy_from_ctx(ctx).enabled


def policy_from_ctx(ctx: Any) -> BatchPolicy:
    temp = _ensure_temp(ctx)
    cfg = getattr(ctx, "cfg", None)
    cfg_batch = getattr(cfg, "batch", None)
    if not isinstance(cfg_batch, Mapping) and hasattr(cfg, "get"):
        cfg_batch = cfg.get("batch")
    policy: dict[str, Any] = {}
    if isinstance(cfg_batch, Mapping):
        policy.update(cfg_batch)
    temp_policy = temp.get("batch_policy")
    if isinstance(temp_policy, Mapping):
        policy.update(temp_policy)
    attr_policy = getattr(ctx, "batch_policy", None)
    if isinstance(attr_policy, Mapping):
        policy.update(attr_policy)
    elif isinstance(attr_policy, bool):
        policy["enabled"] = attr_policy
    if bool(getattr(ctx, "batch_enabled", False)):
        policy["enabled"] = True
    return _coerce_policy(policy)


def _coerce_policy(policy: Mapping[str, Any]) -> BatchPolicy:
    def _int(name: str, default: int) -> int:
        try:
            value = int(policy.get(name, default))
        except Exception:
            value = default
        return value if value > 0 else default

    return BatchPolicy(
        enabled=bool(policy.get("enabled", False)),
        max_size=_int("max_size", int(policy.get("max_count", 64) or 64)),
        max_bytes=_int("max_bytes", 1_048_576),
        max_delay_ms=_int("max_delay_ms", 1),
        admission_timeout_ms=_int("admission_timeout_ms", 5),
        conflict_policy=str(policy.get("conflict_policy", "single_fallback")),
        overflow_policy=str(policy.get("overflow_policy", "backpressure")),
        result_fanout=str(policy.get("result_fanout", "by_admission")),
        allow_reads=bool(policy.get("allow_reads", False)),
        max_queue_depth=_int("max_queue_depth", 1024),
        max_in_flight=_int("max_in_flight", 16),
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
    policy = policy_from_ctx(ctx)
    open_depth = sum(len(group.admissions) for group in state["open"].values())
    if open_depth >= policy.max_queue_depth:
        if policy.overflow_policy == "reject":
            raise RuntimeError("batch admission rejected: max_queue_depth")
        ctx.temp["batch_backpressure"] = True
        if policy.overflow_policy == "scalar_fallback":
            ctx.temp["batch_execution_kind"] = "scalar_fallback"
            ctx.temp["batch_fallback_reason"] = "max_queue_depth"
            intent["force_scalar_fallback"] = True
    group_key = intent["final_group_key"]
    group = state["open"].setdefault(group_key, BatchGroup(group_key=group_key))
    size_bytes = int(intent.get("payload_bytes", 0) or 0)
    admission = BatchAdmission(
        admission_id=next(_next_admission_id),
        group_key=group_key,
        intent=intent,
        sink=transport.get("sink"),
        sink_index=int(transport.get("sink_index", 0) or 0),
        size_bytes=size_bytes,
    )
    admission.result_index = len(group.admissions)
    group.admissions.append(admission)
    group.size_bytes += size_bytes
    state["admission"] = admission
    state["policy"] = policy
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
    policy = policy_from_ctx(ctx)
    max_count = int(policy.max_size)
    max_delay_ns = int(policy.max_delay_ms) * 1_000_000
    age_ns = monotonic_ns() - group.created_ns
    should_seal = (
        len(group.admissions) >= max_count
        or group.size_bytes >= int(policy.max_bytes)
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
