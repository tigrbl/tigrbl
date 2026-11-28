from __future__ import annotations

import inspect
from typing import Any

from tigrbl_atoms.route_handler import (
    HandlerArgument,
    RouteHandlerDeclaration,
    RouteHandlerPlan,
    invoke_route_handler,
)
from tigrbl_typing.protocols import is_dependency_like


def compile_route_handler(
    model: type, alias: str, declaration: RouteHandlerDeclaration
):
    parameters = tuple(inspect.signature(declaration.handler).parameters.values())
    arguments = []
    for parameter in parameters:
        name = parameter.name
        annotation = parameter.annotation
        marker = parameter.default
        if is_dependency_like(marker):
            argument = HandlerArgument(name, "dependency", marker.dependency)
        elif name in {"ctx", "_ctx"} or annotation is dict or annotation is Any:
            argument = HandlerArgument(name, "context")
        elif (
            name in {"request", "_request"}
            or getattr(annotation, "__name__", None) == "Request"
        ):
            argument = HandlerArgument(name, "request")
        elif len(parameters) == 1 and parameter.default is inspect.Parameter.empty:
            argument = HandlerArgument(name, "implicit_request")
        else:
            argument = HandlerArgument(name, "path")
        arguments.append(argument)

    plan = RouteHandlerPlan(model, alias, declaration, tuple(arguments))

    async def step(ctx: Any) -> None:
        await invoke_route_handler(plan, ctx)

    step._tigrbl_route_handler_plan = plan
    step.__tigrbl_label = "hook:wire:tigrbl:route:handler"
    return step
