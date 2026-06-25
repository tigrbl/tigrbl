from __future__ import annotations

import inspect
from types import SimpleNamespace
from typing import Any, Callable

from tigrbl_concrete._concrete._route import ensure_route_ops_model, upsert_route_opspec
from tigrbl_core._spec.binding_spec import (
    FramingSpec,
    framing_kind,
    framing_spec_from_kind,
    WsBindingSpec,
)
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_runtime.channel import normalize_exchange, websocket_adapter


def register_runtime_websocket_route(
    router: Any,
    *,
    path: str,
    alias: str,
    endpoint: Callable[..., Any],
    protocol: str = "ws",
    exchange: str = "bidirectional_stream",
    framing: FramingSpec | str = "text",
    subprotocols: tuple[str, ...] | None = None,
) -> None:
    """Register a websocket endpoint as a runtime-owned operation."""
    model = ensure_route_ops_model(router)
    if model is None:
        return

    normalized_exchange = normalize_exchange(exchange)
    framing_spec = framing_spec_from_kind(framing)
    normalized_framing = framing_kind(framing_spec)
    normalized_subprotocols = tuple(str(value) for value in (subprotocols or ()))
    if normalized_framing == "jsonrpc" and "jsonrpc" not in normalized_subprotocols:
        normalized_subprotocols = (*normalized_subprotocols, "jsonrpc")
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
                framing=framing_spec,
                subprotocols=normalized_subprotocols,
            ),
        ),
    )
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
    setattr(_runtime_websocket_step, "__tigrbl_websocket_endpoint__", endpoint)
    setattr(_runtime_websocket_step, "__tigrbl_websocket_path__", str(path))
    setattr(_runtime_websocket_step, "__tigrbl_websocket_protocol__", str(protocol))
    setattr(
        _runtime_websocket_step,
        "__tigrbl_websocket_exchange__",
        str(normalized_exchange),
    )
    setattr(_runtime_websocket_step, "__tigrbl_websocket_framing__", normalized_framing)
    setattr(
        _runtime_websocket_step,
        "__tigrbl_websocket_subprotocols__",
        normalized_subprotocols,
    )
    setattr(
        _runtime_websocket_step,
        "__tigrbl_websocket_exact__",
        "{" not in str(path) and "}" not in str(path),
    )

    upsert_route_opspec(router, op, handler_step=_runtime_websocket_step)


__all__ = [
    "register_runtime_websocket_route",
]
