from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Egressed
from ...types import Atom, Ctx, EgressedCtx

ANCHOR = _ev.BATCH_FANOUT_EMIT


async def _maybe_await(value: Any) -> Any:
    if hasattr(value, "__await__"):
        return await value
    return value


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    admission = ctx.temp.get("batch_admission")
    payload = ctx.temp.get("fanout_payload")
    if admission is None or payload is None:
        return
    sink = admission.sink
    emit_many = getattr(sink, "emit_many", None)
    if callable(emit_many):
        await _maybe_await(emit_many([payload]))
        return
    emit = getattr(sink, "emit", None)
    if callable(emit):
        await _maybe_await(emit(payload))


class AtomImpl(Atom[Egressed, Egressed, Exception]):
    name = "fanout.emit_many"
    anchor = ANCHOR

    async def __call__(
        self, obj: object | None, ctx: Ctx[Egressed]
    ) -> Ctx[Egressed]:
        await _run(obj, ctx)
        return ctx.promote(EgressedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
