from __future__ import annotations

import json
from typing import Any

from ... import events as _ev
from ...stages import Ingress
from ...types import Atom, Ctx, IngressCtx
from .._temp import _ensure_temp

ANCHOR = _ev.INGRESS_INPUT_PREPARE


def _run(obj: object | None, ctx: Any) -> None:
    del obj
    temp = _ensure_temp(ctx)
    ingress = temp.setdefault("ingress", {})
    hot = temp.setdefault("hot", {})

    body = getattr(ctx, "body", ingress.get("body"))
    if isinstance(body, (bytes, bytearray, memoryview)):
        raw_bytes = hot.get("body_bytes") if isinstance(hot, dict) else None
        if not isinstance(raw_bytes, bytes):
            raw_bytes = bytes(body)
            if isinstance(hot, dict):
                hot["body_bytes"] = raw_bytes
                hot["body_view"] = memoryview(raw_bytes)
        ingress["body_peek"] = raw_bytes[:256]
        content_type = str(
            (getattr(ctx, "headers", {}) or {}).get("content-type", "")
        ).lower()
        if "json" in content_type:
            parsed = hot.get("parsed_json") if isinstance(hot, dict) else None
            loaded = bool(hot.get("parsed_json_loaded")) if isinstance(hot, dict) else False
            if not loaded:
                try:
                    parsed = json.loads(raw_bytes.decode("utf-8"))
                except Exception:
                    parsed = None
                if isinstance(hot, dict):
                    hot["parsed_json"] = parsed
                    hot["parsed_json_loaded"] = True
            if parsed is not None:
                ingress["body_json"] = parsed
    elif body is not None:
        ingress["body_peek"] = str(body)[:256]

    request = getattr(ctx, "request", None)
    if request is not None and body is not None and hasattr(request, "body"):
        request.body = body


class AtomImpl(Atom[Ingress, Ingress, Exception]):
    name = "ingress.input_prepare"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Ingress]) -> Ctx[Ingress]:
        _run(obj, ctx)
        return ctx.promote(IngressCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
