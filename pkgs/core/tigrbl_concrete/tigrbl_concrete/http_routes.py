from __future__ import annotations

import inspect
from dataclasses import replace
from types import SimpleNamespace
from typing import Any, Callable, Iterable

from tigrbl_concrete._concrete._response import Response
from tigrbl_concrete._mapping.model_helpers import _OpSpecGroup
from tigrbl_core._spec.binding_spec import HttpRestBindingSpec
from tigrbl_core._spec.op_spec import OpSpec


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
        tuple(str(item).upper() for item in tuple(getattr(binding, "methods", ()) or ())),
    )


def _merge_http_bindings(existing: tuple[Any, ...], binding: HttpRestBindingSpec) -> tuple[Any, ...]:
    updated: list[Any] = []
    replaced = False
    for current in existing:
        if isinstance(current, HttpRestBindingSpec) and str(getattr(current, "path", "") or "") == binding.path:
            merged_methods = tuple(
                dict.fromkeys(
                    tuple(str(item).upper() for item in tuple(getattr(current, "methods", ()) or ()))
                    + tuple(binding.methods)
                )
            )
            updated.append(replace(current, methods=merged_methods))
            replaced = True
            continue
        updated.append(current)
    if not replaced and _binding_key(binding) not in {_binding_key(item) for item in updated}:
        updated.append(binding)
    return tuple(updated)


def register_http_route(
    owner: Any,
    *,
    path: str,
    methods: Iterable[str],
    alias: str,
    endpoint: Callable[..., Any],
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

    existing_specs = tuple(getattr(getattr(model, "ops", None), "by_alias", {}).get(alias, ()) or ())
    existing = existing_specs[0] if existing_specs else None
    if existing is not None:
        op = replace(
            existing,
            bindings=_merge_http_bindings(tuple(getattr(existing, "bindings", ()) or ()), binding),
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
    updated_ops = SimpleNamespace(all=tuple(retained_specs), by_alias=by_alias, by_key=by_key)
    model.ops = updated_ops
    model.opspecs = updated_ops

    hooks = getattr(model, "hooks", None)
    for alias in removed_aliases:
        if hooks is not None and hasattr(hooks, alias):
            delattr(hooks, alias)


__all__ = ["ensure_system_route_model", "register_http_route"]
