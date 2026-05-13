from __future__ import annotations

from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.BATCH_TRANSPORT_UNIT_CAPTURE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    transport = _ensure_temp(ctx).setdefault("transport", {})
    transport["unit"] = getattr(ctx, "transport_unit", None)
    transport["unit_kind"] = getattr(ctx, "transport_unit_kind", None)
    transport["payload_ref"] = getattr(ctx, "payload_ref", None)
    payload = transport["payload_ref"]
    if isinstance(payload, (bytes, bytearray, memoryview)):
        transport["payload_bytes"] = len(payload)
    elif isinstance(payload, str):
        transport["payload_bytes"] = len(payload.encode("utf-8"))


hot_run = _run


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "transport.unit_capture"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()
setattr(INSTANCE, "__tigrbl_hot_run__", hot_run)

__all__ = ["ANCHOR", "INSTANCE", "hot_run"]
