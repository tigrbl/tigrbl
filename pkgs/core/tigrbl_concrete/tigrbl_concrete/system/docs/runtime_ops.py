from __future__ import annotations

import inspect
import json
from typing import Any, Callable

from tigrbl_concrete._concrete._route import (
    compile_path,
    ensure_route_ops_model,
    upsert_route_opspec,
)
from tigrbl_core._spec.binding_spec import (
    FramingSpec,
    framing_kind,
    framing_spec_from_kind,
    JsonRpcFramingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.op_spec import OpSpec
from tigrbl_runtime.channel import (
    RuntimeWebSocketRoute,
    normalize_exchange,
    websocket_adapter,
)


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
    normalized_path = str(path).rstrip("/") or "/"
    routes = getattr(router, "websocket_routes", None)
    if isinstance(routes, list) and not any(
        getattr(route, "path_template", None) == normalized_path
        and getattr(route, "name", None) == alias
        for route in routes
    ):
        pattern, param_names = compile_path(normalized_path)
        routes.append(
            RuntimeWebSocketRoute(
                path_template=normalized_path,
                pattern=pattern,
                param_names=param_names,
                handler=endpoint,
                name=alias,
                protocol=str(protocol),
                exchange=normalized_exchange,
                framing=normalized_framing,
            )
        )
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
                path=normalized_path,
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


def _jsonrpc_error(
    code: int,
    message: str,
    request_id: Any,
    *,
    data: Any | None = None,
) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "error": error, "id": request_id}


def _jsonrpc_result(result: Any, request_id: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "result": result, "id": request_id}


def _resolve_rpc_target(router: Any, method: str) -> tuple[Any, str] | None:
    table_name, sep, alias = method.partition(".")
    if not sep or not table_name or not alias:
        return None
    tables = getattr(router, "tables", None)
    if isinstance(tables, dict):
        model = tables.get(table_name)
        if isinstance(model, type):
            return model, alias
        for candidate in tables.values():
            if (
                isinstance(candidate, type)
                and getattr(candidate, "__name__", None) == table_name
            ):
                return candidate, alias
    return table_name, alias


async def _dispatch_jsonrpc_payload(router: Any, payload: Any) -> Any:
    if not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0":
        return _jsonrpc_error(-32600, "Invalid Request", None)
    request_id = payload.get("id")
    method = payload.get("method")
    if not isinstance(method, str) or not method:
        return _jsonrpc_error(-32601, "Method not found", request_id)
    target = _resolve_rpc_target(router, method)
    if target is None:
        return _jsonrpc_error(-32601, "Method not found", request_id)
    params = payload.get("params", {})
    if params is None:
        params = {}
    if not isinstance(params, (dict, list, tuple)):
        return _jsonrpc_error(-32602, "Invalid params", request_id)
    model, alias = target
    rpc_call = getattr(router, "rpc_call", None)
    if not callable(rpc_call):
        return _jsonrpc_error(-32603, "Internal error", request_id)
    try:
        result = await rpc_call(
            model,
            alias,
            params,
            ctx={"jsonrpc": payload, "jsonrpc_request_id": request_id},
        )
    except AttributeError:
        return _jsonrpc_error(-32601, "Method not found", request_id)
    except Exception as exc:
        return _jsonrpc_error(
            -32603,
            "Internal error",
            request_id,
            data={"detail": str(exc)},
        )
    if "id" not in payload:
        return None
    return _jsonrpc_result(result, request_id)


async def _dispatch_jsonrpc_text(router: Any, text: str) -> Any:
    try:
        payload = json.loads(text or "")
    except Exception:
        return _jsonrpc_error(-32700, "Parse error", None)
    if isinstance(payload, list):
        responses = []
        for item in payload:
            response = await _dispatch_jsonrpc_payload(router, item)
            if response is not None:
                responses.append(response)
        return responses or None
    return await _dispatch_jsonrpc_payload(router, payload)


def register_websocket_jsonrpc_dispatch_route(
    router: Any,
    *,
    path: str,
    alias: str | None = None,
    protocol: str = "ws",
) -> None:
    """Register a framework-owned WebSocket JSON-RPC dispatcher route."""

    route_alias = alias or f"websocket_jsonrpc:{str(path).strip('/') or 'root'}"

    async def _websocket_jsonrpc_dispatch(websocket: Any) -> None:
        await websocket.accept(subprotocol="jsonrpc")
        while True:
            try:
                text = await websocket.receive_text()
            except RuntimeError:
                break
            response = await _dispatch_jsonrpc_text(router, text)
            if response is None:
                continue
            await websocket.send_text(
                json.dumps(response, separators=(",", ":"), default=str)
            )

    register_runtime_websocket_route(
        router,
        path=path,
        alias=route_alias,
        endpoint=_websocket_jsonrpc_dispatch,
        protocol=protocol,
        framing=JsonRpcFramingSpec(),
        subprotocols=("jsonrpc",),
    )


__all__ = [
    "register_runtime_websocket_route",
    "register_websocket_jsonrpc_dispatch_route",
]
