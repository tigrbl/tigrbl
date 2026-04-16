from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable

from tigrbl_concrete.http_routes import ensure_system_route_model
from tigrbl_core._spec.binding_spec import WsBindingSpec
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup
from tigrbl_runtime.channel import normalize_exchange, websocket_adapter


def register_runtime_websocket_route(
    router: Any,
    *,
    path: str,
    alias: str,
    endpoint: Callable[..., Any],
    protocol: str = "ws",
    exchange: str = "bidirectional_stream",
    framing: str = "text",
) -> None:
    """Register a websocket endpoint as a runtime-owned operation."""
    model = ensure_system_route_model(router)
    if model is None:
        return

    normalized_exchange = normalize_exchange(exchange)
    op = OpSpec(
        alias=alias,
        target="custom",
        arity="collection",
        persist="skip",
        expose_routes=False,
        expose_rpc=False,
        expose_method=False,
        exchange=normalized_exchange,
        subevents=("connect", "receive", "emit", "complete", "disconnect"),
        bindings=(
            WsBindingSpec(
                proto=str(protocol),
                path=path,
                exchange=normalized_exchange,
                framing=str(framing),
            ),
        ),
    )
    ops_ns = getattr(model, "ops", None)
    by_alias = dict(getattr(ops_ns, "by_alias", {}) or {})
    by_alias[alias] = _OpSpecGroup((op,))
    all_specs = tuple(
        spec for spec in tuple(getattr(ops_ns, "all", ()) or ()) if getattr(spec, "alias", None) != alias
    ) + (op,)
    by_key = {
        (str(getattr(spec, "alias", "")), str(getattr(spec, "target", ""))): spec
        for spec in all_specs
    }
    updated_ops = SimpleNamespace(all=all_specs, by_alias=by_alias, by_key=by_key)
    model.ops = updated_ops
    model.opspecs = updated_ops

    async def _runtime_websocket_step(ctx: Any) -> None:
        channel = ctx.get("channel")
        if channel is None:
            raise RuntimeError("runtime websocket step requires channel context")
        websocket = websocket_adapter(channel)
        ctx["websocket"] = websocket
        result = endpoint(websocket)
        if inspect.isawaitable(result):
            result = await result
        if result is not None:
            setattr(ctx, "result", result)
            temp = getattr(ctx, "temp", None)
            if isinstance(temp, dict):
                temp.setdefault("egress", {})["result"] = result

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_runtime_websocket_step]


__all__ = [
    "register_runtime_websocket_route",
]
