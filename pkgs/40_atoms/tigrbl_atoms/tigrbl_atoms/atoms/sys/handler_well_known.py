from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from ... import events as _ev
from ...stages import Operated, Resolved
from ...types import Atom, Ctx, OperatedCtx

ANCHOR = _ev.SYS_HANDLER_PERSISTENCE
TARGET = "well_known"


def _resources_for_model(model: Any) -> Mapping[str, Any]:
    resources = getattr(model, "__tigrbl_well_known_resources__", None)
    return resources if isinstance(resources, Mapping) else {}


def _headers_for(media_type: str, headers: Any) -> dict[str, str]:
    merged = {"content-type": media_type}
    if isinstance(headers, Mapping):
        merged.update({str(key): str(value) for key, value in headers.items()})
    return merged


def _body_for(payload: Any, media_type: str) -> bytes:
    if media_type == "application/json":
        return json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
    if isinstance(payload, bytes):
        return payload
    if isinstance(payload, bytearray):
        return bytes(payload)
    if isinstance(payload, memoryview):
        return payload.tobytes()
    return str(payload).encode("utf-8")


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    op = str(getattr(ctx, "op", "") or "")
    resource = _resources_for_model(getattr(ctx, "model", None)).get(op)
    if not isinstance(resource, Mapping):
        raise RuntimeError(f"Well-known resource metadata unavailable for {op!r}.")

    media_type = str(resource.get("media_type") or "application/json")
    response = {
        "status_code": int(resource.get("status_code") or 200),
        "headers": _headers_for(media_type, resource.get("headers")),
        "body": _body_for(resource.get("payload"), media_type),
    }
    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    if isinstance(egress, dict):
        egress["transport_response"] = response
    setattr(ctx, "transport_response", response)


class AtomImpl(Atom[Resolved, Operated, Exception]):
    name = "sys.handler_well_known"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Resolved]) -> Ctx[Operated]:
        await _run(obj, ctx)
        return ctx.promote(OperatedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "TARGET", "INSTANCE"]
