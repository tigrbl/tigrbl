from __future__ import annotations

from ...types import Atom, Ctx, EncodedCtx
from ...stages import Failed, Encoded

import json
from typing import Any, Mapping

from ... import events as _ev
from tigrbl_typing.status import create_standardized_error

ANCHOR = _ev.OUT_DUMP


def _jsonrpc_request_id(ctx: Any) -> Any:
    for source in (
        getattr(ctx, "body", None),
        getattr(getattr(ctx, "request", None), "body", None),
        getattr(getattr(ctx, "request", None), "_body", None),
        getattr(getattr(ctx, "request", None), "_json", None),
    ):
        payload = source
        if isinstance(payload, (bytes, bytearray)):
            try:
                payload = json.loads(bytes(payload).decode("utf-8"))
            except Exception:
                payload = None
        if isinstance(payload, dict) and payload.get("jsonrpc") == "2.0":
            return payload.get("id")

    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        if "jsonrpc_request_id" in temp:
            return temp.get("jsonrpc_request_id")
        for key in ("route", "dispatch"):
            section = temp.get(key)
            if not isinstance(section, dict):
                continue
            for subkey in ("rpc_envelope", "rpc"):
                payload = section.get(subkey)
                if isinstance(payload, dict) and payload.get("jsonrpc") == "2.0":
                    return payload.get("id")
    return None


def _is_jsonrpc_request(ctx: Any) -> bool:
    temp = getattr(ctx, "temp", None)
    if isinstance(temp, dict):
        route = temp.get("route")
        if isinstance(route, dict):
            rpc_env = route.get("rpc_envelope")
            if isinstance(rpc_env, dict) and rpc_env.get("jsonrpc") == "2.0":
                return True

        dispatch = temp.get("dispatch")
        if isinstance(dispatch, dict):
            rpc = dispatch.get("rpc")
            if isinstance(rpc, dict) and rpc.get("jsonrpc") == "2.0":
                return True

    raw = getattr(ctx, "gw_raw", None) or getattr(ctx, "raw", None)
    path = getattr(raw, "path", None)
    app = getattr(ctx, "app", None)
    prefix = getattr(app, "jsonrpc_prefix", None)
    if isinstance(path, str) and isinstance(prefix, str):
        return (path.rstrip("/") or "/") == (prefix.rstrip("/") or "/")
    return False


async def _run(obj: object | None, ctx: Any) -> None:
    del obj
    err = getattr(ctx, "error", None)
    if err is None:
        return

    std = create_standardized_error(err)
    detail = std.detail if getattr(std, "detail", None) not in (None, "") else str(std)
    status_code = int(getattr(std, "status_code", 500) or 500)

    temp = getattr(ctx, "temp", None)
    if not isinstance(temp, dict):
        temp = {}
        setattr(ctx, "temp", temp)
    egress = temp.setdefault("egress", {})
    if _is_jsonrpc_request(ctx):
        from tigrbl_typing.status.mappings import ERROR_MESSAGES, _HTTP_TO_RPC

        rpc_code = _HTTP_TO_RPC.get(status_code, -32603)
        data = dict(detail) if isinstance(detail, Mapping) else {"detail": detail}
        egress["transport_response"] = {
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "body": {
                "jsonrpc": "2.0",
                "error": {
                    "code": rpc_code,
                    "message": ERROR_MESSAGES.get(rpc_code, "Internal error"),
                    "data": data,
                },
                "id": _jsonrpc_request_id(ctx),
            },
        }
        setattr(ctx, "status_code", 200)
        return

    egress["transport_response"] = {
        "status_code": status_code,
        "headers": {"content-type": "application/json"},
        "body": {"detail": detail},
    }
    setattr(ctx, "status_code", status_code)


class AtomImpl(Atom[Failed, Encoded, Exception]):
    name = "response.error_to_transport"
    anchor = ANCHOR

    async def __call__(self, obj: object | None, ctx: Ctx[Failed]) -> Ctx[Encoded]:
        await _run(obj, ctx)
        return ctx.promote(EncodedCtx)


INSTANCE = AtomImpl()

__all__ = ["ANCHOR", "INSTANCE"]
