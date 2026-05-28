from __future__ import annotations

import importlib
from collections import OrderedDict
from dataclasses import replace
from typing import Any

from tigrbl_core._spec.docs_spec import DocsPayloadSpec, DocsUixSpec
from tigrbl_core._spec.path_spec import PathSpec
from tigrbl_concrete._concrete import engine_resolver as _resolver
from tigrbl_concrete._concrete.tigrbl_router import TigrblRouter

from .engine_lowering import install_scope_engine_names


def lower_appspec_routers(app: Any, spec: Any) -> None:
    routers = tuple(getattr(spec, "routers", ()) or ())
    if not routers:
        return

    for router_spec in routers:
        router = TigrblRouter(
            engine=getattr(router_spec, "engine", None),
            jsonrpc_prefix=getattr(spec, "jsonrpc_prefix", "/rpc"),
            system_prefix=getattr(spec, "system_prefix", "/system"),
            execution_backend=getattr(spec, "execution_backend", None),
        )
        setattr(router, "name", getattr(router_spec, "name", "router"))
        setattr(router, "engine_name", getattr(router_spec, "engine_name", None))
        setattr(router, "_tigrbl_route_prefix", _normalize_prefix(getattr(router_spec, "prefix", "")))
        setattr(router, "_tigrbl_path_specs", tuple(getattr(router_spec, "paths", ()) or ()))
        setattr(router, "_tigrbl_docs_payloads", _collect_docs_payloads(router._tigrbl_path_specs))
        setattr(router, "_tigrbl_docs_uix", _collect_docs_uix(router._tigrbl_path_specs))

        install_scope_engine_names(router=router)
        _lower_router_paths(router, router_spec)
        app.include_router(router, prefix=getattr(router_spec, "prefix", None))


def _lower_router_paths(router: Any, router_spec: Any) -> None:
    resource_mounts: OrderedDict[str, tuple[Any, Any, str]] = OrderedDict()
    rpc_tables: OrderedDict[tuple[str, str], tuple[Any, Any]] = OrderedDict()

    for path_spec in tuple(getattr(router_spec, "paths", ()) or ()):
        if path_spec.kind == "resource":
            for table_spec in tuple(path_spec.tables or ()):
                model = _resolve_table_model(table_spec)
                _apply_table_spec_to_model(model, table_spec)
                key = _model_identity(model, table_spec)
                resource_mounts.setdefault(key, (model, table_spec, path_spec.path))
                install_scope_engine_names(
                    router=router,
                    model=model,
                    table_spec=table_spec,
                    op_specs=tuple(getattr(table_spec, "ops", ()) or ()),
                )
        elif path_spec.kind == "jsonrpc":
            for table_spec in tuple(path_spec.tables or ()):
                model = _resolve_table_model(table_spec)
                _apply_table_spec_to_model(model, table_spec)
                key = (path_spec.path, _model_identity(model, table_spec))
                rpc_tables.setdefault(key, (model, table_spec))
                install_scope_engine_names(
                    router=router,
                    model=model,
                    table_spec=table_spec,
                    op_specs=tuple(getattr(table_spec, "ops", ()) or ()),
                )
        elif path_spec.kind == "docs-payload":
            _mount_docs_payload(router, path_spec)
        elif path_spec.kind == "docs-uix":
            _mount_docs_uix(router, path_spec)
        elif path_spec.kind == "static":
            directory = str((path_spec.static or {}).get("directory") or "")
            if directory:
                router.mount_static(directory=directory, path=path_spec.path)
        elif path_spec.kind == "mount":
            mounted = getattr(path_spec, "mount", None)
            if mounted is not None:
                from tigrbl_concrete._concrete.tigrbl_app import TigrblApp

                nested = mounted if hasattr(mounted, "__call__") and hasattr(mounted, "routes") else TigrblApp.from_spec(mounted)
                router.mount_app(app=nested, path=path_spec.path)

    for model, table_spec, fallback_prefix in resource_mounts.values():
        _, materialized_router = router.include_table(
            model,
            prefix=None if _has_explicit_rest_paths(table_spec) else fallback_prefix,
        )
        engine_name = getattr(table_spec, "engine_name", None) or getattr(
            router, "engine_name", None
        )
        if materialized_router is not None and engine_name is not None:
            _resolver.register_router_engine_name(materialized_router, engine_name)

    if rpc_tables:
        mounted_dispatchers: set[str] = set()
        for (dispatcher_path, _), payload in rpc_tables.items():
            model, table_spec = payload
            _, materialized_router = router.include_table(model, mount_router=False)
            install_scope_engine_names(
                router=router,
                model=model,
                table_spec=table_spec,
                op_specs=tuple(getattr(table_spec, "ops", ()) or ()),
            )
            engine_name = getattr(table_spec, "engine_name", None) or getattr(
                router, "engine_name", None
            )
            if materialized_router is not None and engine_name is not None:
                _resolver.register_router_engine_name(materialized_router, engine_name)
            if dispatcher_path not in mounted_dispatchers:
                router.mount_jsonrpc(prefix=dispatcher_path)
                mounted_dispatchers.add(dispatcher_path)


def _mount_docs_payload(router: Any, path_spec: PathSpec) -> None:
    payload = path_spec.docs_payload
    if not isinstance(payload, DocsPayloadSpec):
        return
    if payload.kind == "openapi":
        router.mount_openapi(path=path_spec.path)
    elif payload.kind == "openrpc":
        router.mount_openrpc(path=path_spec.path)
    elif payload.kind == "jsonschema":
        router.mount_json_schema(path=path_spec.path)
    elif str(payload.kind) == "asyncapi":
        raise NotImplementedError("AsyncAPI docs payloads are not supported.")


def _mount_docs_uix(router: Any, path_spec: PathSpec) -> None:
    uix = path_spec.docs_uix
    if not isinstance(uix, DocsUixSpec):
        return
    if uix.kind == "swagger":
        router.mount_swagger(path=path_spec.path)
    elif uix.kind == "lens":
        router.mount_lens(path=path_spec.path, spec_path=uix.payload_path)
    else:
        raise NotImplementedError(f"Docs UIX kind {uix.kind!r} is not supported by canonical lowering.")


def _resolve_table_model(table_spec: Any) -> Any:
    model = getattr(table_spec, "model", None)
    if isinstance(model, type):
        return model

    model_ref = getattr(table_spec, "model_ref", None) or model
    if not isinstance(model_ref, str) or not model_ref:
        raise ValueError("Canonical path lowering requires TableSpec.model_ref or a materialized model.")

    if ":" in model_ref:
        module_name, attr_name = model_ref.split(":", 1)
    else:
        module_name, attr_name = model_ref.rsplit(".", 1)
    module = importlib.import_module(module_name)
    resolved = getattr(module, attr_name)
    if not isinstance(resolved, type):
        raise TypeError(f"Resolved model_ref {model_ref!r} is not a class.")
    return resolved


def _collect_docs_payloads(paths: tuple[PathSpec, ...]) -> dict[str, DocsPayloadSpec]:
    return {
        path.path: path.docs_payload
        for path in paths
        if path.kind == "docs-payload" and isinstance(path.docs_payload, DocsPayloadSpec)
    }


def _collect_docs_uix(paths: tuple[PathSpec, ...]) -> dict[str, DocsUixSpec]:
    return {
        path.path: path.docs_uix
        for path in paths
        if path.kind == "docs-uix" and isinstance(path.docs_uix, DocsUixSpec)
    }


def _model_identity(model: Any, table_spec: Any) -> str:
    if isinstance(model, type):
        return f"{model.__module__}:{model.__name__}"
    model_ref = getattr(table_spec, "model_ref", None)
    if isinstance(model_ref, str) and model_ref:
        return model_ref
    return str(getattr(table_spec, "name", "table"))


def _normalize_prefix(prefix: str | None) -> str:
    if not prefix:
        return ""
    token = str(prefix)
    if not token.startswith("/"):
        token = f"/{token}"
    return token.rstrip("/")


def _has_explicit_rest_paths(table_spec: Any) -> bool:
    for op_spec in tuple(getattr(table_spec, "ops", ()) or ()):
        for binding in tuple(getattr(op_spec, "bindings", ()) or ()):
            if str(getattr(binding, "proto", "") or "") != "http.rest":
                continue
            if str(getattr(binding, "path", "") or "").strip():
                return True
    return False


def _apply_table_spec_to_model(model: Any, table_spec: Any) -> None:
    resource = getattr(table_spec, "resource", None)
    if isinstance(resource, str) and resource:
        setattr(model, "resource_name", resource)

    declared = tuple(getattr(model, "__tigrbl_ops__", ()) or ())
    incoming = tuple(getattr(table_spec, "ops", ()) or ())
    if not incoming:
        return

    merged: OrderedDict[tuple[str, str], Any] = OrderedDict()
    for spec in declared:
        key = (str(getattr(spec, "alias", "")), str(getattr(spec, "target", "")))
        if key == ("", ""):
            continue
        merged[key] = spec
    for spec in incoming:
        key = (str(getattr(spec, "alias", "")), str(getattr(spec, "target", "")))
        if key == ("", ""):
            continue
        existing = merged.get(key)
        if existing is None:
            merged[key] = replace(spec, table=model)
            continue
        existing_bindings = tuple(getattr(existing, "bindings", ()) or ())
        new_bindings = tuple(getattr(spec, "bindings", ()) or ())
        if new_bindings:
            combined_bindings = tuple(
                dict.fromkeys((*existing_bindings, *new_bindings))
            )
            merged[key] = replace(
                spec,
                table=model,
                bindings=combined_bindings,
            )
        else:
            merged[key] = replace(spec, table=model)
    setattr(model, "__tigrbl_ops__", tuple(merged.values()))
