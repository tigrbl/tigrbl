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
    payloads = ctx.temp.get("fanout_payloads")
    if payloads:
        grouped: dict[int, tuple[Any, list[Any]]] = {}
        for admission, payload in payloads:
            sink = getattr(admission, "sink", None)
            key = id(sink)
            if key not in grouped:
                grouped[key] = (sink, [])
            grouped[key][1].append(payload)
        for sink, items in grouped.values():
            await _emit_to_sink(sink, items)
        return
    admission = ctx.temp.get("batch_admission")
    payload = ctx.temp.get("fanout_payload")
    if admission is None or payload is None:
        return
    await _emit_to_sink(admission.sink, [payload])


async def _emit_to_sink(sink: Any, payloads: list[Any]) -> None:
    emit_many = getattr(sink, "emit_many", None)
    if callable(emit_many):
        await _maybe_await(emit_many(payloads))
        return
    emit = getattr(sink, "emit", None)
    if callable(emit):
        for payload in payloads:
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
