from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Guarded
from ...types import Atom, Ctx, GuardedCtx
from .._temp import _ensure_temp

ANCHOR = _ev.BATCH_GROUP_KEY


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    intent = _ensure_temp(ctx).setdefault("intent", {})
    model = intent.get("model")
    intent["final_group_key"] = (
        getattr(ctx, "engine_id", None),
        getattr(ctx, "tenant_id", None),
        getattr(ctx, "principal_id", None),
        getattr(ctx, "tx_policy", None),
        getattr(ctx, "conflict_domain", None),
        intent.get("op"),
        getattr(model, "__name__", None),
        intent.get("sink_family"),
    )


hot_run = _run


class AtomImpl(Atom[Guarded, Guarded, Exception]):
    name = "intent.final_group_key"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Guarded]) -> Ctx[Guarded]:
        _run(obj, ctx)
        return ctx.promote(GuardedCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
