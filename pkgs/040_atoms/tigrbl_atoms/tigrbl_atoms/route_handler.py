from __future__ import annotations

import inspect
from contextlib import AsyncExitStack, aclosing, closing
from dataclasses import dataclass
from typing import Any, Callable, Literal

from .atoms.egress.to_transport_response import project_handler_result


@dataclass(frozen=True, slots=True)
class RouteHandlerDeclaration:
    handler: Callable[..., Any]
    request_adapter: Callable[[Any], Any]
    status_code: int | None


@dataclass(frozen=True, slots=True)
class HandlerArgument:
    name: str
    source: Literal["dependency", "context", "request", "implicit_request", "path"]
    dependency: Callable[..., Any] | None = None


@dataclass(frozen=True, slots=True)
class RouteHandlerPlan:
    model: type
    alias: str
    declaration: RouteHandlerDeclaration
    arguments: tuple[HandlerArgument, ...]


async def _dependency_value(stack: AsyncExitStack, resolver: Callable[[], Any]) -> Any:
    value = resolver()
    if inspect.isasyncgen(value):
        generator = await stack.enter_async_context(aclosing(value))
        try:
            return await anext(generator)
        except StopAsyncIteration as exc:
            raise RuntimeError("Async dependency did not yield a value.") from exc
    if inspect.isgenerator(value):
        generator = stack.enter_context(closing(value))
        try:
            return next(generator)
        except StopIteration as exc:
            raise RuntimeError("Dependency did not yield a value.") from exc
    if inspect.isawaitable(value):
        return await value
    return value


async def invoke_route_handler(plan: RouteHandlerPlan, ctx: Any) -> None:
    declaration = plan.declaration
    path_params = ctx.get("path_params") or {}
    async with AsyncExitStack() as stack:
        arguments = {}
        request = None
        for argument in plan.arguments:
            name = argument.name
            if name in path_params:
                arguments[name] = path_params[name]
            elif argument.source == "dependency":
                owner = ctx.get("app") or ctx.get("router")
                overrides = getattr(owner, "dependency_overrides", {}) or {}
                resolver = overrides.get(argument.dependency, argument.dependency)
                arguments[name] = await _dependency_value(stack, resolver)
            elif argument.source == "context":
                arguments[name] = ctx
            elif argument.source == "request":
                if request is None:
                    request = declaration.request_adapter(ctx)
                arguments[name] = request
            elif argument.source == "implicit_request" and not path_params:
                arguments[name] = ctx.get("request")

        if declaration.status_code is not None:
            ctx.status_code = declaration.status_code
        result = declaration.handler(**arguments)
        if inspect.isawaitable(result):
            result = await result
        project_handler_result(ctx, result)
