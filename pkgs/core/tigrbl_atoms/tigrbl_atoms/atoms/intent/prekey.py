from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_INPUT_PREPARE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    intent = _ensure_temp(ctx).setdefault("intent", {})
    model = intent.get("model")
    intent["prekey"] = (
        intent.get("op"),
        getattr(model, "__name__", None),
        intent.get("sink_family"),
    )


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "intent.prekey"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
