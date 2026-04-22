"""API route datatypes, normalization, and owner-local route-op helpers."""

from __future__ import annotations

import inspect
import re
from dataclasses import dataclass, replace
from types import SimpleNamespace
from typing import Annotated, Any, Callable, Iterable, Sequence, get_args, get_origin

from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup
from tigrbl_concrete.security.dependencies import Dependency
from tigrbl_core._spec.binding_spec import (
    HttpRestBindingSpec,
    HttpStreamBindingSpec,
    SseBindingSpec,
    WebTransportBindingSpec,
    WsBindingSpec,
)
from tigrbl_core._spec.op_spec import OpSpec

from ._response import Response

Handler = Callable[..., Any]

ROUTE_OPS_MODEL_NAME = "__tigrbl_route_ops__"
ROUTE_OPS_RESOURCE_NAME = "route_ops"
JSONRPC_MOUNT_SENTINEL = object()


@dataclass(frozen=True)
class Route:
    methods: frozenset[str]
    path_template: str
    pattern: re.Pattern[str]
    param_names: tuple[str, ...]
    handler: Handler
    name: str
    summary: str | None = None
    description: str | None = None
    tags: list[str] | None = None
    deprecated: bool = False
    request_schema: dict[str, Any] | None = None
    response_schema: dict[str, Any] | None = None
    path_param_schemas: dict[str, dict[str, Any]] | None = None
    query_param_schemas: dict[str, dict[str, Any]] | None = None
    include_in_schema: bool = True
    operation_id: str | None = None
    response_model: Any | None = None
    request_model: Any | None = None
    responses: dict[int, dict[str, Any]] | None = None
    status_code: int | None = None
    dependencies: list[Any] | None = None
    security_dependencies: list[Any] | None = None
    inherit_owner_dependencies: bool = True
    tigrbl_model: Any | None = None
    tigrbl_alias: str | None = None
    tigrbl_binding: Any | None = None
    tigrbl_exchange: str | None = None
    tigrbl_tx_scope: str | None = None

    @property
    def path(self) -> str:
        if self.path_template == "/":
            return "/"
        return self.path_template.rstrip("/")

    @property
    def endpoint(self) -> Handler:
        return self.handler

    @property
    def dependant(self) -> Any:
        def _param(name: str) -> SimpleNamespace:
            return SimpleNamespace(name=name)

        path_param_names = set(self.param_names)
        path_params = [_param(name) for name in self.param_names]
        query_params: list[SimpleNamespace] = []
        dependencies: list[SimpleNamespace] = []

        signature = inspect.signature(self.handler)
        for param in signature.parameters.values():
            if param.name in path_param_names:
                continue

            dep_callable = None
            default = param.default
            if isinstance(default, Dependency):
                dep_callable = default.dependency

            annotation = param.annotation
            if dep_callable is None and get_origin(annotation) is Annotated:
                for meta in get_args(annotation)[1:]:
                    if isinstance(meta, Dependency):
                        dep_callable = meta.dependency
                        break

            if dep_callable is not None:
                dependencies.append(_param(param.name))
                continue

            if param.kind in {
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            }:
                query_params.append(_param(param.name))

        for dep in self.dependencies or []:
            dep_fn = getattr(dep, "dependency", dep)
            dep_name = getattr(dep_fn, "__name__", None) or "dependency"
            dependencies.append(_param(dep_name))

        return SimpleNamespace(
            path_params=path_params,
            query_params=query_params,
            dependencies=dependencies,
        )


def compile_path(path_template: str) -> tuple[re.Pattern[str], tuple[str, ...]]:
    if not path_template.startswith("/"):
        path_template = "/" + path_template

    normalized_path = path_template.rstrip("/") or "/"
    param_names: list[str] = []

    def repl(match: re.Match[str]) -> str:
        name = match.group(1)
        param_names.append(name)
        return rf"(?P<{name}>[^/]+)"

    pattern_src = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", repl, normalized_path)
    if normalized_path != "/":
        pattern_src += "/?"
    pattern = re.compile("^" + pattern_src + "$")
    return pattern, tuple(param_names)


def normalize_prefix(prefix: str) -> str:
    value = str(prefix or "").strip()
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


def normalize_methods(methods: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        str(method).upper()
        for method in methods
        if str(method).strip() and str(method).upper() not in {"HEAD", "OPTIONS"}
    )
    if not normalized:
        raise ValueError("methods must include at least one HTTP verb")
    return normalized


def ensure_route_ops_model(owner: Any) -> type | None:
    tables = getattr(owner, "tables", None)
    if not isinstance(tables, dict):
        return None

    model = tables.get(ROUTE_OPS_MODEL_NAME)
    if model is None:
        model = type("TigrblRouteOps", (), {})
        model.resource_name = ROUTE_OPS_RESOURCE_NAME
        model.hooks = SimpleNamespace()
        ops_ns = SimpleNamespace(all=(), by_alias={}, by_key={})
        model.ops = ops_ns
        model.opspecs = ops_ns
        tables[ROUTE_OPS_MODEL_NAME] = model
    return model


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


def _prefix_transport_binding(binding: Any, mount_prefix: str) -> Any:
    if not mount_prefix or not isinstance(
        binding,
        (
            HttpRestBindingSpec,
            HttpStreamBindingSpec,
            SseBindingSpec,
            WsBindingSpec,
            WebTransportBindingSpec,
        ),
    ):
        return binding

    path = str(getattr(binding, "path", "") or "")
    if not path.startswith("/"):
        path = f"/{path}"
    prefixed_path = (
        path if path == mount_prefix or path.startswith(f"{mount_prefix}/") else f"{mount_prefix}{path}"
    )
    if prefixed_path == getattr(binding, "path", None):
        return binding
    return replace(binding, path=prefixed_path)


def _rebuild_ops_namespace(specs: Sequence[OpSpec]) -> SimpleNamespace:
    grouped_specs: dict[str, list[OpSpec]] = {}
    by_key: dict[tuple[str, str], OpSpec] = {}
    for spec in tuple(specs):
        grouped_specs.setdefault(spec.alias, []).append(spec)
        by_key[(spec.alias, spec.target)] = spec
    by_alias = {
        alias: _OpSpecGroup(tuple(specs_for_alias))
        for alias, specs_for_alias in grouped_specs.items()
    }
    return SimpleNamespace(all=tuple(specs), by_alias=by_alias, by_key=by_key)


def _route_request(route: Route, ctx: Any) -> Any:
    request = getattr(ctx, "request", None)
    if request is not None:
        return request
    if isinstance(ctx, dict):
        return ctx.get("request")
    getter = getattr(ctx, "get", None)
    if callable(getter):
        return getter("request")
    return None


def _route_path_params(route: Route, ctx: Any) -> dict[str, Any]:
    if isinstance(ctx, dict):
        values = ctx.get("path_params")
        return dict(values or {})
    getter = getattr(ctx, "get", None)
    if callable(getter):
        values = getter("path_params")
        return dict(values or {})
    values = getattr(ctx, "path_params", None)
    return dict(values or {})


def _build_route_step(route: Route) -> Handler:
    async def _route_step(ctx: Any) -> None:
        request = _route_request(route, ctx)
        path_params = _route_path_params(route, ctx)
        kwargs: dict[str, Any] = {}
        signature = inspect.signature(route.handler)
        params = list(signature.parameters.items())
        for name, param in params:
            if name in path_params:
                kwargs[name] = path_params[name]
                continue
            default = param.default
            dep_callable = getattr(default, "dependency", None)
            if callable(dep_callable):
                owner = getattr(ctx, "app", None) or getattr(ctx, "router", None)
                overrides = getattr(owner, "dependency_overrides", {}) or {}
                resolver = overrides.get(dep_callable, dep_callable)
                resolved = resolver()
                if inspect.isawaitable(resolved):
                    resolved = await resolved
                kwargs[name] = resolved
                continue
            annotation = param.annotation
            if (
                name in {"ctx", "_ctx"}
                or annotation is dict
                or annotation is Any
            ):
                kwargs[name] = ctx
                continue
            if (
                name in {"request", "_request"}
                or getattr(annotation, "__name__", None) == "Request"
                or (
                    len(params) == 1
                    and not path_params
                    and param.default is inspect._empty
                )
            ):
                kwargs[name] = request

        response = route.handler(**kwargs) if kwargs else route.handler()
        if inspect.isawaitable(response):
            response = await response

        if isinstance(response, Response):
            payload = {
                "status_code": int(getattr(response, "status_code", 200) or 200),
                "headers": dict(getattr(response, "headers", ()) or ()),
                "body": (
                    response
                    if hasattr(response, "body_iterator")
                    else getattr(response, "body", b"")
                ),
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

    return _route_step


def upsert_route_opspec(
    owner: Any,
    spec: OpSpec,
    *,
    handler_step: Handler | None = None,
) -> None:
    model = ensure_route_ops_model(owner)
    if model is None:
        return

    ops_ns = getattr(model, "ops", None)
    existing_specs = tuple(getattr(ops_ns, "all", ()) or ())
    updated_specs = tuple(
        current for current in existing_specs if getattr(current, "alias", None) != spec.alias
    ) + (spec,)
    updated_ops = _rebuild_ops_namespace(updated_specs)
    model.ops = updated_ops
    model.opspecs = updated_ops

    if handler_step is None:
        return

    hooks_ns = getattr(model.hooks, spec.alias, None)
    if hooks_ns is None:
        hooks_ns = SimpleNamespace()
        setattr(model.hooks, spec.alias, hooks_ns)
    hooks_ns.HANDLER = [handler_step]


def prune_route_ops(owner: Any, *paths: str) -> None:
    model = ensure_route_ops_model(owner)
    if model is None:
        return

    path_set = {
        (path if str(path).startswith("/") else f"/{path}").rstrip("/") or "/"
        for path in paths
    }
    ops = tuple(getattr(getattr(model, "opspecs", None), "all", ()) or ())
    if not ops:
        return

    retained_specs: list[OpSpec] = []
    removed_aliases: set[str] = set()
    for op in ops:
        bindings = tuple(getattr(op, "bindings", ()) or ())
        filtered_bindings = tuple(
            binding
            for binding in bindings
            if str(getattr(binding, "path", "") or "") not in path_set
        )
        if not filtered_bindings:
            removed_aliases.add(str(getattr(op, "alias", "")))
            continue
        if filtered_bindings != bindings:
            retained_specs.append(replace(op, bindings=filtered_bindings))
        else:
            retained_specs.append(op)

    updated_ops = _rebuild_ops_namespace(retained_specs)
    model.ops = updated_ops
    model.opspecs = updated_ops

    hooks = getattr(model, "hooks", None)
    for alias in removed_aliases:
        if hooks is not None and hasattr(hooks, alias):
            delattr(hooks, alias)


def add_route(
    owner: Any,
    path: str,
    endpoint: Handler,
    *,
    methods: Sequence[str],
    **kwargs: Any,
) -> Route:
    normalized_methods = normalize_methods(methods)
    base_prefix = normalize_prefix(getattr(owner, "prefix", ""))
    if not path.startswith("/"):
        path = f"/{path}"
    full_path = f"{base_prefix}{path}" if base_prefix else path
    normalized_path = full_path.rstrip("/") or "/"
    pattern, param_names = compile_path(normalized_path)

    binding = kwargs.pop("tigrbl_binding", None)
    if binding is None:
        binding = HttpRestBindingSpec(
            proto="http.rest",
            path=normalized_path,
            methods=normalized_methods,
        )

    route = Route(
        methods=frozenset(normalized_methods),
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
        inherit_owner_dependencies=bool(
            kwargs.pop("inherit_owner_dependencies", True)
        ),
        tigrbl_model=kwargs.pop("tigrbl_model", None),
        tigrbl_alias=kwargs.pop("tigrbl_alias", None),
        tigrbl_binding=binding,
        tigrbl_exchange=kwargs.pop("tigrbl_exchange", None),
        tigrbl_tx_scope=kwargs.pop("tigrbl_tx_scope", None),
    )
    owner.routes.append(route)

    if route.tigrbl_model is None:
        alias = route.tigrbl_alias or route.name
        existing_ops = getattr(ensure_route_ops_model(owner), "ops", None)
        existing_specs = tuple(getattr(existing_ops, "by_alias", {}).get(alias, ()) or ())
        existing = existing_specs[0] if existing_specs else None
        tags = tuple(route.tags or ())
        if isinstance(route.tigrbl_binding, HttpRestBindingSpec):
            bindings = (
                _merge_http_bindings(
                    tuple(getattr(existing, "bindings", ()) or ()),
                    route.tigrbl_binding,
                )
                if existing is not None
                else (route.tigrbl_binding,)
            )
        else:
            bindings = tuple(getattr(existing, "bindings", ()) or ())
            if route.tigrbl_binding is not None:
                bindings = bindings + (route.tigrbl_binding,)

        route_spec = (
            replace(
                existing,
                bindings=tuple(bindings),
                tags=tags or tuple(getattr(existing, "tags", ()) or ()),
                status_code=route.status_code
                if route.status_code is not None
                else getattr(existing, "status_code", None),
                request_model=route.request_model or getattr(existing, "request_model", None),
                response_model=route.response_model or getattr(existing, "response_model", None),
                handler=route.endpoint,
            )
            if existing is not None
            else OpSpec(
                alias=alias,
                target="custom",
                arity="collection",
                persist="skip",
                expose_routes=False,
                expose_rpc=False,
                bindings=tuple(bindings),
                tags=tags,
                status_code=route.status_code,
                request_model=route.request_model,
                response_model=route.response_model,
                exchange=str(route.tigrbl_exchange or "request_response"),
                tx_scope=str(route.tigrbl_tx_scope or "inherit"),
                handler=route.endpoint,
            )
        )
        upsert_route_opspec(owner, route_spec, handler_step=_build_route_step(route))

    return route


async def _jsonrpc_mount_marker(*_args: Any, **_kwargs: Any) -> None:
    """Marker endpoint; JSON-RPC execution is selected by binding dispatch."""
    return None


def add_jsonrpc_mount(
    owner: Any,
    path: str,
    *,
    endpoint: str,
    name: str = "jsonrpc",
) -> Route | None:
    if not path.startswith("/"):
        path = f"/{path}"
    normalized_path = path.rstrip("/") or "/"

    mounts = getattr(owner, "_jsonrpc_endpoint_mounts", None)
    if not isinstance(mounts, dict):
        mounts = {}
        setattr(owner, "_jsonrpc_endpoint_mounts", mounts)
    mounts[normalized_path] = endpoint
    if normalized_path != "/":
        mounts[f"{normalized_path}/"] = endpoint

    for existing in getattr(owner, "routes", ()) or ():
        if getattr(existing, "path", None) == normalized_path:
            return existing

    pattern, param_names = compile_path(normalized_path)
    route = Route(
        methods=frozenset({"POST"}),
        path_template=normalized_path,
        pattern=pattern,
        param_names=param_names,
        handler=_jsonrpc_mount_marker,
        name=name,
        include_in_schema=False,
        inherit_owner_dependencies=False,
        tigrbl_model=JSONRPC_MOUNT_SENTINEL,
        tigrbl_exchange="request_response",
        tigrbl_tx_scope="skip",
    )
    owner.routes.append(route)
    return route


def include_router_routes(owner: Any, router: Any, *, prefix: str = "") -> None:
    nested_prefix = normalize_prefix(prefix)
    router_dependencies = list(getattr(router, "dependencies", ()) or ())
    for route in getattr(router, "routes", ()):
        path = route.path_template
        if nested_prefix:
            path = f"{nested_prefix}{path}" if path != "/" else nested_prefix

        route_dependencies = list(getattr(route, "dependencies", ()) or ())
        merged_dependencies = route_dependencies
        if getattr(route, "inherit_owner_dependencies", True):
            merged_dependencies = [
                dep for dep in router_dependencies if dep not in route_dependencies
            ] + route_dependencies

        normalized_path = (path if path.startswith("/") else f"/{path}").rstrip("/") or "/"
        methods = frozenset(str(method).upper() for method in tuple(route.methods))
        owner.routes[:] = [
            existing
            for existing in getattr(owner, "routes", ())
            if not (
                getattr(existing, "path", None) == normalized_path
                and frozenset(
                    str(method).upper()
                    for method in tuple(getattr(existing, "methods", ()) or ())
                )
                == methods
            )
        ]
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
            inherit_owner_dependencies=route.inherit_owner_dependencies,
            tigrbl_model=route.tigrbl_model,
            tigrbl_alias=route.tigrbl_alias,
            tigrbl_binding=_prefix_transport_binding(route.tigrbl_binding, nested_prefix),
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


def prefix_model_bindings(model: type, mount_prefix: str) -> None:
    if not mount_prefix:
        return

    ops_ns = getattr(model, "ops", None)
    specs = tuple(getattr(ops_ns, "all", ()) or ())
    if not specs:
        return

    updated_specs: list[OpSpec] = []
    changed = False
    for spec in specs:
        bindings = tuple(getattr(spec, "bindings", ()) or ())
        updated_bindings: list[Any] = []
        local_changed = False
        for binding in bindings:
            if not isinstance(
                binding,
                (
                    HttpRestBindingSpec,
                    HttpStreamBindingSpec,
                    SseBindingSpec,
                    WsBindingSpec,
                    WebTransportBindingSpec,
                ),
            ):
                updated_bindings.append(binding)
                continue

            path = str(getattr(binding, "path", "") or "")
            if not path.startswith("/"):
                path = f"/{path}"
            prefixed = _prefix_transport_binding(binding, mount_prefix)
            if prefixed is not binding:
                local_changed = True
                updated_bindings.append(prefixed)
            else:
                updated_bindings.append(binding)

        if local_changed:
            changed = True
            updated_specs.append(replace(spec, bindings=tuple(updated_bindings)))
        else:
            updated_specs.append(spec)

    if not changed:
        return

    updated_ops = _rebuild_ops_namespace(updated_specs)
    model.ops = updated_ops
    model.opspecs = updated_ops


__all__ = [
    "ROUTE_OPS_MODEL_NAME",
    "Route",
    "add_jsonrpc_mount",
    "add_route",
    "compile_path",
    "ensure_route_ops_model",
    "include_router_routes",
    "merge_tags",
    "normalize_methods",
    "normalize_prefix",
    "prefix_model_bindings",
    "prune_route_ops",
    "route",
    "upsert_route_opspec",
]
