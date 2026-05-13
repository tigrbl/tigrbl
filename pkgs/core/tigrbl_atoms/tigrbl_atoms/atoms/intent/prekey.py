from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Bound
from ...types import Atom, BoundCtx, Ctx
from .._temp import _ensure_temp

ANCHOR = _ev.BATCH_PREKEY


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    intent = _ensure_temp(ctx).setdefault("intent", {})
    model = intent.get("model")
    intent["prekey"] = (
        intent.get("op"),
        getattr(model, "__name__", None),
        intent.get("sink_family"),
    )


hot_run = _run


class AtomImpl(Atom[Bound, Bound, Exception]):
    name = "intent.prekey"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Bound]) -> Ctx[Bound]:
        _run(obj, ctx)
        return ctx.promote(BoundCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
