"""Shared route registration helpers for concrete app and router classes."""

from __future__ import annotations

import inspect
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Iterable, Sequence

from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup
from tigrbl_concrete.system.docs.openapi.metadata import (
    is_metadata_route as _is_metadata_route,
)
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core._spec.op_spec import OpSpec

from ._response import Response
from ._route import Route, compile_path

Handler = Callable[..., Any]


def ensure_system_route_model(owner: Any) -> type | None:
    """Return the synthetic model that stores concrete route-backed ops."""
    tables = getattr(owner, "tables", None)
    if not isinstance(tables, dict):
        return None

    model_name = "__tigrbl_system_routes__"
    model = tables.get(model_name)
    if model is None:
        model = type("TigrblSystemRoutes", (), {})
        model.resource_name = "system_routes"
        model.hooks = SimpleNamespace()
        ops_ns = SimpleNamespace(all=(), by_alias={}, by_key={})
        model.ops = ops_ns
        model.opspecs = ops_ns
        tables[model_name] = model
    return model


def _normalize_methods(methods: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        str(method).upper()
        for method in methods
        if str(method).strip() and str(method).upper() not in {"HEAD", "OPTIONS"}
    )
    if not normalized:
        raise ValueError("methods must include at least one HTTP verb")
    return normalized


def _binding_key(binding: Any) -> tuple[str, str, tuple[str, ...]]:
    return (
        str(getattr(binding, "proto", "") or ""),
        str(getattr(binding, "path", "") or ""),
        tuple(
            str(item).upper()
            for item in tuple(getattr(binding, "methods", ()) or ())
        ),
    )


def _merge_http_bindings(
    existing: tuple[Any, ...],
    binding: HttpRestBindingSpec,
) -> tuple[Any, ...]:
    updated: list[Any] = []
    replaced = False
    for current in existing:
        if (
            isinstance(current, HttpRestBindingSpec)
            and str(getattr(current, "path", "") or "") == binding.path
        ):
            merged_methods = tuple(
                dict.fromkeys(
                    tuple(
                        str(item).upper()
                        for item in tuple(getattr(current, "methods", ()) or ())
                    )
                    + tuple(binding.methods)
                )
            )
            updated.append(replace(current, methods=merged_methods))
            replaced = True
            continue
        updated.append(current)
    if not replaced and _binding_key(binding) not in {
        _binding_key(item) for item in updated
    }:
        updated.append(binding)
    return tuple(updated)


def register_http_route(
    owner: Any,
    *,
    path: str,
    methods: Iterable[str],
    alias: str,
    endpoint: Callable[..., Any],
    tags: Sequence[str] | None = None,
) -> None:
    """Register an HTTP route as a concrete custom op with HTTP binding specs."""
    model = ensure_system_route_model(owner)
    if model is None:
        return

    normalized_path = str(path or "/")
    if not normalized_path.startswith("/"):
        normalized_path = f"/{normalized_path}"
    normalized_path = normalized_path.rstrip("/") or "/"
    normalized_methods = _normalize_methods(methods)
    binding = HttpRestBindingSpec(
        proto="http.rest",
        path=normalized_path,
        methods=normalized_methods,
    )

    ops_ns = getattr(model, "ops", None)
    existing_specs = tuple(getattr(ops_ns, "by_alias", {}).get(alias, ()) or ())
    existing = existing_specs[0] if existing_specs else None
    normalized_tags = tuple(tags or ())

    if existing is not None:
        op = replace(
            existing,
            bindings=_merge_http_bindings(
                tuple(getattr(existing, "bindings", ()) or ()),
                binding,
            ),
            tags=normalized_tags or tuple(getattr(existing, "tags", ()) or ()),
        )
    else:
        op = OpSpec(
            alias=alias,
            target="custom",
            arity="collection",
            persist="skip",
            expose_routes=False,
            expose_rpc=False,
            bindings=(binding,),
            tags=normalized_tags,
        )

    by_alias = dict(getattr(ops_ns, "by_alias", {}) or {})
    by_alias[alias] = _OpSpecGroup((op,))
    all_specs = tuple(
        spec
        for spec in tuple(getattr(ops_ns, "all", ()) or ())
        if getattr(spec, "alias", None) != alias
    ) + (op,)
    by_key = {
        (str(getattr(spec, "alias", "")), str(getattr(spec, "target", ""))): spec
        for spec in all_specs
    }
    updated_ops = SimpleNamespace(all=all_specs, by_alias=by_alias, by_key=by_key)
    model.ops = updated_ops
    model.opspecs = updated_ops

    async def _route_step(ctx: Any) -> None:
        request = getattr(ctx, "request", None)
        try:
            response = endpoint()
        except TypeError:
            try:
                response = endpoint(request)
            except TypeError:
                response = endpoint(ctx)
        if inspect.isawaitable(response):
            response = await response

        if isinstance(response, Response):
            payload = {
                "status_code": int(getattr(response, "status_code", 200) or 200),
                "headers": dict(getattr(response, "headers", ()) or ()),
                "body": getattr(response, "body", b""),
            }
            temp = getattr(ctx, "temp", None)
            if isinstance(temp, dict):
                temp.setdefault("route", {})["short_circuit"] = True
                temp.setdefault("egress", {})["transport_response"] = payload
                temp["egress"]["suppress_asgi_send"] = True
            setattr(ctx, "transport_response", payload)
            return

        setattr(ctx, "result", response)
        temp = getattr(ctx, "temp", None)
        if isinstance(temp, dict):
            temp.setdefault("egress", {})["result"] = response

    hooks_ns = getattr(model.hooks, alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, alias, hooks_ns)
    hooks_ns.HANDLER = [_route_step]


def remove_http_routes(owner: Any, *paths: str) -> None:
    """Remove registered concrete route ops whose bindings match any path."""
    model = ensure_system_route_model(owner)
    if model is None:
        return

    path_set = {
        (path if str(path).startswith("/") else f"/{path}").rstrip("/") or "/"
        for path in paths
    }
    ops = tuple(getattr(getattr(model, "opspecs", None), "all", ()) or ())
    if not ops:
        return

    retained_specs: list[Any] = []
    removed_aliases: set[str] = set()
    for op in ops:
        bindings = tuple(getattr(op, "bindings", ()) or ())
        filtered_bindings = tuple(
            binding
            for binding in bindings
            if str(getattr(binding, "path", "") or "") not in path_set
        )
        if not filtered_bindings:
            alias = getattr(op, "alias", None)
            if isinstance(alias, str):
                removed_aliases.add(alias)
            continue
        if filtered_bindings != bindings:
            retained_specs.append(replace(op, bindings=filtered_bindings))
        else:
            retained_specs.append(op)

    by_alias: dict[str, Any] = {}
    by_key: dict[tuple[str, str], Any] = {}
    for spec in retained_specs:
        alias = str(getattr(spec, "alias", ""))
        by_alias[alias] = _OpSpecGroup((spec,))
        by_key[(alias, str(getattr(spec, "target", "")))] = spec
    updated_ops = SimpleNamespace(
        all=tuple(retained_specs),
        by_alias=by_alias,
        by_key=by_key,
    )
    model.ops = updated_ops
    model.opspecs = updated_ops

    hooks = getattr(model, "hooks", None)
    for alias in removed_aliases:
        if hooks is not None and hasattr(hooks, alias):
            delattr(hooks, alias)


def normalize_prefix(prefix: str) -> str:
    value = (prefix or "").strip()
    if not value:
        return ""
    if not value.startswith("/"):
        value = f"/{value}"
    return value.rstrip("/") or ""


def merge_tags(
    base: Sequence[str] | None,
    extra: Sequence[str] | None,
) -> list[str] | None:
    if base is None and extra is None:
        return None
    merged = list(base or ())
    for tag in extra or ():
        if tag not in merged:
            merged.append(tag)
    return merged


def add_route(
    owner: Any,
    path: str,
    endpoint: Handler,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> None:
    method_set = frozenset(str(m).upper() for m in methods)
    if not method_set:
        raise ValueError("methods must include at least one HTTP verb")

    base_prefix = normalize_prefix(getattr(owner, "prefix", ""))
    if not path.startswith("/"):
        path = f"/{path}"
    full_path = f"{base_prefix}{path}" if base_prefix else path
    normalized_path = full_path.rstrip("/") or "/"
    pattern, param_names = compile_path(normalized_path)

    route = Route(
        methods=method_set,
        path_template=normalized_path,
        pattern=pattern,
        param_names=param_names,
        handler=endpoint,
        name=kwargs.pop("name", getattr(endpoint, "__name__", "route")),
        summary=kwargs.pop("summary", None),
        description=kwargs.pop("description", None),
        tags=merge_tags(getattr(owner, "tags", None), kwargs.pop("tags", None)),
        deprecated=bool(kwargs.pop("deprecated", False)),
        request_schema=kwargs.pop("request_schema", None),
        response_schema=kwargs.pop("response_schema", None),
        path_param_schemas=kwargs.pop("path_param_schemas", None),
        query_param_schemas=kwargs.pop("query_param_schemas", None),
        include_in_schema=kwargs.pop("include_in_schema", True),
        operation_id=kwargs.pop("operation_id", None),
        response_model=kwargs.pop("response_model", None),
        request_model=kwargs.pop("request_model", None),
        responses=kwargs.pop("responses", None),
        status_code=kwargs.pop("status_code", None),
        dependencies=kwargs.pop("dependencies", None),
        security_dependencies=kwargs.pop("security_dependencies", None),
        tigrbl_model=kwargs.pop("tigrbl_model", None),
        tigrbl_alias=kwargs.pop("tigrbl_alias", None),
        tigrbl_binding=kwargs.pop("tigrbl_binding", None),
        tigrbl_exchange=kwargs.pop("tigrbl_exchange", None),
        tigrbl_tx_scope=kwargs.pop("tigrbl_tx_scope", None),
    )
    owner.routes.append(route)

    # Keep custom HTTP routes visible through the same concrete op/binding
    # surface that powers compiled-plan dispatch and system-document builders.
    if route.tigrbl_model is None:
        register_http_route(
            owner,
            path=route.path,
            methods=tuple(route.methods),
            alias=route.name,
            endpoint=route.endpoint,
            tags=tuple(route.tags or ()),
        )


def include_router(owner: Any, router: Any, *, prefix: str = "") -> None:
    nested_prefix = normalize_prefix(prefix)
    router_dependencies = list(getattr(router, "dependencies", ()) or ())
    for route in getattr(router, "routes", ()):
        path = route.path_template
        if nested_prefix:
            path = f"{nested_prefix}{path}" if path != "/" else nested_prefix

        route_dependencies = list(getattr(route, "dependencies", ()) or ())
        if _is_metadata_route(router, route):
            merged_dependencies = route_dependencies
        else:
            merged_dependencies = [
                dep for dep in router_dependencies if dep not in route_dependencies
            ] + route_dependencies

        add_route(
            owner,
            path,
            route.handler,
            methods=tuple(route.methods),
            name=route.name,
            summary=route.summary,
            description=route.description,
            tags=route.tags,
            deprecated=route.deprecated,
            request_schema=route.request_schema,
            response_schema=route.response_schema,
            path_param_schemas=route.path_param_schemas,
            query_param_schemas=route.query_param_schemas,
            include_in_schema=route.include_in_schema,
            operation_id=route.operation_id,
            response_model=route.response_model,
            request_model=route.request_model,
            responses=route.responses,
            status_code=route.status_code,
            dependencies=merged_dependencies,
            security_dependencies=route.security_dependencies,
            tigrbl_model=route.tigrbl_model,
            tigrbl_alias=route.tigrbl_alias,
            tigrbl_binding=route.tigrbl_binding,
            tigrbl_exchange=route.tigrbl_exchange,
            tigrbl_tx_scope=route.tigrbl_tx_scope,
        )


def route(
    owner: Any,
    path: str,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> Callable[[Handler], Handler]:
    def _decorator(handler: Handler) -> Handler:
        add_route(owner, path, handler, methods=methods, **kwargs)
        return handler

    return _decorator


__all__ = [
    "add_route",
    "ensure_system_route_model",
    "include_router",
    "merge_tags",
    "normalize_prefix",
    "register_http_route",
    "remove_http_routes",
    "route",
]
