from __future__ import annotations

import asyncio
from collections import defaultdict
from itertools import count
from time import monotonic_ns
from typing import Any, Mapping

from .._temp import _ensure_temp
from ..sys import _oltp_context as _ctx
from ..hot.slots import HotSlotPayload, project_present_dict
from ._scheduler import policy_from_ctx
from ._types import BatchAdmission, BatchGroup


class ResidentBatchScheduler:
    """Atom-owned scheduler that coalesces admissions across request contexts."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._open: dict[tuple[Any, ...], BatchGroup] = {}
        self._ctx_by_admission: dict[int, Any] = {}
        self._seal_tasks: dict[tuple[Any, ...], asyncio.Task[None]] = {}
        self._in_flight = 0
        self._next_admission_id = count(1)
        self.metrics: dict[str, int] = defaultdict(int)

    async def admit(self, ctx: Any) -> BatchAdmission:
        policy = policy_from_ctx(ctx)
        if not policy.enabled:
            raise RuntimeError("batch admission requested while batching is disabled")

        temp = _ensure_temp(ctx)
        intent = temp["intent"]
        transport = temp.get("transport", {})
        group_key = intent["final_group_key"]
        size_bytes = int(intent.get("payload_bytes", 0) or 0)

        async with self._lock:
            if self._queued_depth_unlocked() >= int(policy.max_queue_depth):
                if policy.overflow_policy == "reject":
                    raise RuntimeError("batch admission rejected: max_queue_depth")
                temp["batch_backpressure"] = True
                if policy.overflow_policy == "scalar_fallback":
                    temp["batch_execution_kind"] = "scalar_fallback"
                    temp["batch_fallback_reason"] = "max_queue_depth"
                    intent["force_scalar_fallback"] = True

            group = self._open.setdefault(group_key, BatchGroup(group_key=group_key))
            admission = BatchAdmission(
                admission_id=next(self._next_admission_id),
                group_key=group_key,
                intent=intent,
                sink=transport.get("sink"),
                sink_index=int(transport.get("sink_index", 0) or 0),
                size_bytes=size_bytes,
                slot_payload=intent.get("slot_payload"),
                future=asyncio.get_running_loop().create_future(),
                op=intent.get("op"),
                target=intent.get("target"),
                model=intent.get("model"),
                payload_ref=intent.get("payload_ref"),
                statement=intent.get("statement"),
                correlation_id=intent.get("correlation_id"),
                force_seal=bool(intent.get("force_seal")),
            )
            admission.result_index = len(group.admissions)
            if group.owner_admission_id is None:
                group.owner_admission_id = admission.admission_id
            group.admissions.append(admission)
            group.size_bytes += size_bytes
            self._ctx_by_admission[admission.admission_id] = ctx
            temp["batch_admission"] = admission
            temp["batch_group"] = group
            temp["batch_resident_admitted"] = True

            self.metrics["admitted"] += 1
            if self._should_seal_unlocked(group, policy, admission):
                await self._seal_unlocked(group.group_key)
            else:
                self._ensure_timer_unlocked(group.group_key, policy.max_delay_ms)
            return admission

    async def await_result(self, ctx: Any) -> Any:
        admission = _ensure_temp(ctx).get("batch_admission")
        if admission is None:
            return None
        future = getattr(admission, "future", None)
        if future is None:
            return None
        return await future

    def _queued_depth_unlocked(self) -> int:
        return sum(len(group.admissions) for group in self._open.values())

    def _should_seal_unlocked(
        self, group: BatchGroup, policy: Any, admission: BatchAdmission
    ) -> bool:
        max_delay_ns = int(policy.max_delay_ms) * 1_000_000
        return (
            len(group.admissions) >= int(policy.max_size)
            or group.size_bytes >= int(policy.max_bytes)
            or monotonic_ns() - group.created_ns >= max_delay_ns
            or admission.force_seal
        )

    def _ensure_timer_unlocked(self, group_key: tuple[Any, ...], delay_ms: int) -> None:
        if group_key in self._seal_tasks:
            return
        self._seal_tasks[group_key] = asyncio.create_task(
            self._seal_after_delay(group_key, delay_ms)
        )

    async def _seal_after_delay(
        self, group_key: tuple[Any, ...], delay_ms: int
    ) -> None:
        try:
            await asyncio.sleep(max(int(delay_ms), 0) / 1000)
            async with self._lock:
                await self._seal_unlocked(group_key)
        finally:
            self._seal_tasks.pop(group_key, None)

    async def _seal_unlocked(self, group_key: tuple[Any, ...]) -> None:
        group = self._open.pop(group_key, None)
        if group is None or group.sealed:
            return
        group.sealed = True
        self.metrics["sealed"] += 1
        asyncio.create_task(self._execute_group(group))

    async def _execute_group(self, group: BatchGroup) -> None:
        self._in_flight += 1
        try:
            await self._execute_group_inner(group)
        except Exception as exc:  # pragma: no cover - exercised via slots
            group.error_slots = [exc for _ in group.admissions]
            group.result_slots = [None for _ in group.admissions]
        finally:
            for admission in group.admissions:
                ctx = self._ctx_by_admission.pop(admission.admission_id, None)
                if ctx is not None:
                    _finalize_ctx(ctx, group, admission)
                future = getattr(admission, "future", None)
                if future is not None and not future.done():
                    error = _slot(group.error_slots, admission.result_index)
                    if error is not None:
                        future.set_exception(error)
                    else:
                        future.set_result(_slot(group.result_slots, admission.result_index))
            self._in_flight -= 1

    async def _execute_group_inner(self, group: BatchGroup) -> None:
        owner_ctx = self._owner_ctx(group)
        if owner_ctx is None:
            group.result_slots = [None for _ in group.admissions]
            return
        db, release, owns_db = await _acquire_batch_db(owner_ctx)
        try:
            if owns_db:
                await _begin_if_available(db)
            await self._execute_with_db(group, db)
            if owns_db:
                await _commit_if_available(db)
                self.metrics["commits"] += 1
        except Exception:
            if owns_db:
                await _rollback_if_available(db)
                self.metrics["rollbacks"] += 1
            raise
        finally:
            if release is not None:
                await _maybe_await(release())

    async def _execute_with_db(self, group: BatchGroup, db: Any) -> None:
        statements = [admission.statement for admission in group.admissions]
        parameter_sets = [
            _payload_for_execution(admission) for admission in group.admissions
        ]
        first = statements[0] if statements else None

        if (
            statements
            and all(statement == first for statement in statements)
            and first is not None
        ):
            executemany = getattr(db, "executemany", None)
            if callable(executemany):
                group.result_slots = _as_slots(
                    await _maybe_await(executemany(first, parameter_sets))
                )
                group.error_slots = [None for _ in group.admissions]
                self.metrics["executemany"] += 1
                return

        if statements and all(statement is not None for statement in statements):
            executeloop = getattr(db, "executeloop", None)
            if callable(executeloop):
                group.result_slots = _as_slots(
                    await _maybe_await(executeloop(list(zip(statements, parameter_sets))))
                )
                group.error_slots = [None for _ in group.admissions]
                self.metrics["executeloop"] += 1
                return

        if _is_create_group(group):
            result = await _execute_create_many(group, db, parameter_sets)
            if result is None:
                group.fallback = True
                group.fallback_reason = "unsupported_executemany"
                group.result_slots = [None for _ in group.admissions]
                group.error_slots = [None for _ in group.admissions]
                self.metrics["fallback"] += 1
                return
            group.result_slots = result
            group.error_slots = [None for _ in group.admissions]
            self.metrics["executemany"] += 1
            return

        group.fallback = True
        group.fallback_reason = "unsupported_resident_batch"
        group.result_slots = [None for _ in group.admissions]
        group.error_slots = [None for _ in group.admissions]
        self.metrics["fallback"] += 1

    def _owner_ctx(self, group: BatchGroup) -> Any | None:
        owner_id = group.owner_admission_id
        if owner_id is not None:
            ctx = self._ctx_by_admission.get(owner_id)
            if ctx is not None:
                return ctx
        for admission in group.admissions:
            ctx = self._ctx_by_admission.get(admission.admission_id)
            if ctx is not None:
                return ctx
        return None


def get_resident_scheduler(ctx: Any) -> ResidentBatchScheduler | None:
    temp = _ensure_temp(ctx)
    scheduler = temp.get("batch_scheduler")
    if isinstance(scheduler, ResidentBatchScheduler):
        return scheduler
    scheduler = getattr(ctx, "batch_scheduler", None)
    if isinstance(scheduler, ResidentBatchScheduler):
        temp["batch_scheduler"] = scheduler
        return scheduler
    return None


def _finalize_ctx(ctx: Any, group: BatchGroup, admission: BatchAdmission) -> None:
    temp = _ensure_temp(ctx)
    temp["batch_group"] = group
    temp["batch_admission"] = admission
    temp["batch_resident_handled"] = True
    temp["batch_resident_tx_owned"] = True
    temp["batch_execution_kind"] = "resident"
    temp["batch_raw_results"] = group.result_slots
    setattr(ctx, "result", _slot(group.result_slots, admission.result_index))


def _slot(slots: list[Any], index: int | None) -> Any:
    if index is None:
        return None
    try:
        return slots[index]
    except IndexError:
        return None


def _as_slots(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _acquire_batch_db(ctx: Any) -> tuple[Any, Any | None, bool]:
    temp = _ensure_temp(ctx)
    acquire = temp.get("batch_db_acquire")
    if not callable(acquire):
        acquire = getattr(ctx, "batch_db_acquire", None)
    if callable(acquire):
        acquired = await _maybe_await(acquire(ctx))
        if isinstance(acquired, tuple):
            if len(acquired) >= 2:
                return acquired[0], acquired[1], True
            if len(acquired) == 1:
                return acquired[0], None, True
        return acquired, None, True
    return _ctx.db(ctx), None, False


async def _begin_if_available(db: Any) -> None:
    begin = getattr(db, "begin", None)
    if callable(begin):
        await _maybe_await(begin())


async def _commit_if_available(db: Any) -> None:
    commit = getattr(db, "commit", None)
    if callable(commit):
        await _maybe_await(commit())


async def _rollback_if_available(db: Any) -> None:
    rollback = getattr(db, "rollback", None)
    if callable(rollback):
        await _maybe_await(rollback())


def _is_create_group(group: BatchGroup) -> bool:
    if not group.admissions:
        return False
    first_model = group.admissions[0].model
    if not isinstance(first_model, type):
        return False
    for admission in group.admissions:
        op = str(admission.op or "").lower()
        target = str(admission.target or op).lower()
        payload = _payload_for_execution(admission)
        if admission.model is not first_model:
            return False
        if target != "create":
            return False
        if not isinstance(payload, Mapping):
            return False
    return True


def _payload_for_execution(admission: BatchAdmission) -> Any:
    payload = admission.payload_ref
    if isinstance(payload, Mapping):
        return payload
    slot_payload = getattr(admission, "slot_payload", None)
    if isinstance(slot_payload, HotSlotPayload):
        return project_present_dict(slot_payload)
    return payload


async def _execute_create_many(
    group: BatchGroup, db: Any, parameter_sets: list[Any]
) -> list[Any] | None:
    execute = getattr(db, "execute", None)
    if not callable(execute):
        return None
    try:
        from sqlalchemy import insert as sa_insert
        from tigrbl_ops_oltp.crud.ops import _filter_in_values
        from tigrbl_ops_oltp.crud.helpers import _validate_enum_values
    except Exception:
        return None

    model = group.admissions[0].model
    if not isinstance(model, type):
        return None
    rows = []
    for payload in parameter_sets:
        if not isinstance(payload, Mapping):
            return None
        row = _filter_in_values(model, payload, "create")
        _validate_enum_values(model, row)
        rows.append(row)
    if not rows:
        return []

    stmt = sa_insert(model).returning(model)
    result = await _maybe_await(execute(stmt, rows))
    scalars = getattr(result, "scalars", None)
    if callable(scalars):
        scalar_result = scalars()
        all_rows = getattr(scalar_result, "all", None)
        if callable(all_rows):
            return list(all_rows())
    all_rows = getattr(result, "all", None)
    if callable(all_rows):
        return [row[0] if isinstance(row, tuple) and row else row for row in all_rows()]
    return None


__all__ = ["ResidentBatchScheduler", "get_resident_scheduler"]
