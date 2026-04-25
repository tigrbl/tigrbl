from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from types import SimpleNamespace
from typing import Any

from tigrbl_core.config.constants import (
    TIGRBL_DEFAULT_ROOT_ALIAS,
    TIGRBL_DEFAULT_ROOT_METHOD,
    TIGRBL_DEFAULT_ROOT_PATH,
)


def _table_iter(app: Any) -> tuple[Any, ...]:
    tables = getattr(app, "tables", None)
    if isinstance(tables, dict):
        return tuple(v for v in tables.values() if isinstance(v, type))
    if isinstance(tables, Sequence) and not isinstance(
        tables, (str, bytes, bytearray)
    ):
        return tuple(tables)
    return ()


def _opspecs(model: Any) -> tuple[Any, ...]:
    ops = getattr(getattr(model, "opspecs", SimpleNamespace()), "all", ()) or ()
    if ops:
        return tuple(ops)

    table_ops = getattr(model, "ops", None)
    if table_ops is not None:
        by_alias = getattr(table_ops, "by_alias", None)
        if isinstance(by_alias, Mapping) and by_alias:
            flattened: list[Any] = []
            for specs in by_alias.values():
                if specs is None:
                    continue
                if isinstance(specs, Sequence) and not isinstance(
                    specs, (str, bytes, bytearray)
                ):
                    flattened.extend(tuple(specs))
                    continue
                alias = getattr(specs, "alias", None)
                target = getattr(specs, "target", None)
                if alias is not None and target is not None:
                    flattened.append(specs)
            if flattened:
                return tuple(flattened)
        all_ops = getattr(table_ops, "all", ()) or ()
        if all_ops:
            return tuple(all_ops)
        if isinstance(table_ops, Sequence) and not isinstance(
            table_ops, (str, bytes, bytearray)
        ):
            return tuple(table_ops)

    declared_ops = getattr(model, "__tigrbl_ops__", ()) or ()
    if declared_ops:
        return tuple(declared_ops)

    return ()


def _as_mapping(app: Any) -> dict[str, Any]:
    if isinstance(app, str):
        payload = json.loads(app)
        if not isinstance(payload, dict):
            raise TypeError("rust runtime expects a mapping or JSON object")
        return payload
    if isinstance(app, Mapping):
        return dict(app)
    return {
        "name": getattr(
            app,
            "name",
            getattr(
                app,
                "title",
                getattr(app, "TITLE", app.__class__.__name__),
            ),
        ),
        "title": getattr(
            app,
            "title",
            getattr(
                app,
                "name",
                getattr(app, "TITLE", app.__class__.__name__),
            ),
        ),
        "version": getattr(app, "version", getattr(app, "VERSION", "0.1.0")),
        "jsonrpc_prefix": getattr(app, "jsonrpc_prefix", "/rpc"),
        "system_prefix": getattr(app, "system_prefix", "/system"),
        "bindings": list(getattr(app, "bindings", []) or []),
        "tables": list(getattr(app, "tables", []) or []),
        "engines": list(getattr(app, "engines", []) or []),
        "callbacks": list(getattr(app, "callbacks", []) or []),
        "runtime": dict(getattr(app, "runtime_config", {}) or {}),
        "metadata": dict(getattr(app, "metadata", {}) or {}),
        "engine": getattr(app, "engine", None),
    }


def _machine_name(source: dict[str, Any], app: Any) -> str:
    raw = (
        source.get("name")
        or getattr(app, "name", None)
        or source.get("title")
        or getattr(app, "title", None)
        or getattr(app, "TITLE", None)
        or app.__class__.__name__
    )
    return str(raw).strip()


def _table_name(table: Any) -> str:
    for attr in ("__tablename__", "__resource__", "resource_name", "name"):
        value = getattr(table, attr, None)
        if callable(value):
            try:
                value = value()
            except Exception:
                value = None
        if isinstance(value, str) and value:
            return value
    model = getattr(table, "model", None)
    if isinstance(model, type):
        return _table_name(model)
    if isinstance(model, str) and model:
        return model.rsplit(":", 1)[-1].rsplit(".", 1)[-1].lower()
    model_ref = getattr(table, "model_ref", None)
    if isinstance(model_ref, str) and model_ref:
        return model_ref.rsplit(":", 1)[-1].rsplit(".", 1)[-1].lower()
    return getattr(table, "__name__", table.__class__.__name__).lower()


def _iter_tables(source: dict[str, Any], app: Any) -> tuple[Any, ...]:
    raw = source.get("tables")
    if raw is None:
        return _table_iter(app)
    if isinstance(raw, Mapping):
        return tuple(raw.values())
    if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        return tuple(raw)
    raise TypeError("rust runtime expects app.tables to be a mapping or sequence")


def _normalize_transport(proto: str) -> str:
    mapping = {
        "http.rest": "rest",
        "https.rest": "rest",
        "http.jsonrpc": "jsonrpc",
        "https.jsonrpc": "jsonrpc",
        "http.stream": "stream",
        "https.stream": "stream",
        "http.sse": "sse",
        "https.sse": "sse",
        "ws": "ws",
        "wss": "ws",
        "webtransport": "webtransport",
    }
    return mapping.get(proto, proto or "rest")


def _normalize_path(path: Any) -> str:
    return str(path or "/").rstrip("/") or "/"


def _is_default_root_binding(binding: Mapping[str, Any]) -> bool:
    return (
        binding.get("transport") == "rest"
        and _normalize_path(binding.get("path")) == "/"
    )


def _has_root_binding(bindings: list[dict[str, Any]]) -> bool:
    return any(_is_default_root_binding(binding) for binding in bindings)


def _default_root_binding() -> dict[str, Any]:
    return {
        "alias": TIGRBL_DEFAULT_ROOT_ALIAS,
        "transport": "rest",
        "family": "rest",
        "framing": None,
        "path": TIGRBL_DEFAULT_ROOT_PATH,
        "methods": (TIGRBL_DEFAULT_ROOT_METHOD,),
        "op": {
            "name": TIGRBL_DEFAULT_ROOT_ALIAS,
            "kind": "read",
            "route": TIGRBL_DEFAULT_ROOT_PATH,
            "exchange": "request_response",
            "tx_scope": "inherit",
            "subevents": [],
        },
        "table": {"name": TIGRBL_DEFAULT_ROOT_ALIAS},
    }


def _binding_path(binding: Any, *, jsonrpc_prefix: str) -> str:
    path = getattr(binding, "path", None)
    if isinstance(path, str) and path:
        return path
    rpc_method = getattr(binding, "rpc_method", None)
    if isinstance(rpc_method, str) and rpc_method:
        prefix = jsonrpc_prefix.rstrip("/") or "/rpc"
        return f"{prefix}/{rpc_method}"
    return "/"


def _binding_methods(binding: Any, target: str) -> tuple[str, ...]:
    methods = tuple(
        str(item).upper() for item in (getattr(binding, "methods", ()) or ())
    )
    if methods:
        return methods
    default = {
        "create": ("POST",),
        "read": ("GET",),
        "list": ("GET",),
        "delete": ("DELETE",),
        "replace": ("PUT",),
        "update": ("PATCH",),
        "merge": ("PATCH",),
    }
    return default.get(target, ("POST",))


def _lower_declared_bindings(source: dict[str, Any], app: Any) -> list[dict[str, Any]]:
    raw = source.get("bindings")
    if raw is not None:
        if not (
            isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray))
        ):
            raise TypeError("rust runtime expects app.bindings to be a sequence")
        if raw and all(isinstance(item, Mapping) for item in raw):
            payload: list[dict[str, Any]] = [dict(item) for item in raw]
            if not _has_root_binding(payload):
                payload.append(_default_root_binding())
            return payload

    payload: list[dict[str, Any]] = []
    jsonrpc_prefix = str(source.get("jsonrpc_prefix", "/rpc") or "/rpc")

    for table in _iter_tables(source, app):
        table_name = _table_name(table)
        for spec in _opspecs(table):
            alias = str(getattr(spec, "alias", getattr(spec, "target", "")) or "")
            target = str(getattr(spec, "target", alias) or alias)
            exchange = str(
                getattr(spec, "exchange", "request_response") or "request_response"
            )
            tx_scope = str(getattr(spec, "tx_scope", "inherit") or "inherit")
            subevents = [
                str(item) for item in tuple(getattr(spec, "subevents", ()) or ())
            ]
            for binding in tuple(getattr(spec, "bindings", ()) or ()):
                proto = str(getattr(binding, "proto", "") or "")
                transport = _normalize_transport(proto)
                path = _binding_path(binding, jsonrpc_prefix=jsonrpc_prefix)
                methods = _binding_methods(binding, target)
                payload.append(
                    {
                        "alias": alias,
                        "transport": transport,
                        "family": "bidirectional"
                        if transport in {"ws", "webtransport"}
                        else transport,
                        "framing": getattr(binding, "framing", None),
                        "path": path,
                        "methods": methods,
                        "op": {
                            "name": alias,
                            "kind": target,
                            "route": path,
                            "exchange": str(
                                getattr(binding, "exchange", exchange) or exchange
                            ),
                            "tx_scope": tx_scope,
                            "subevents": subevents,
                        },
                        "table": {"name": table_name},
                    }
                )
    if not _has_root_binding(payload):
        payload.append(_default_root_binding())
    return payload


def _lower_declared_tables(source: dict[str, Any], app: Any) -> list[dict[str, str]]:
    raw = source.get("tables")
    if raw is not None:
        if not (
            isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray))
        ):
            raise TypeError("rust runtime expects app.tables to be a sequence")
        if raw and all(isinstance(item, Mapping) for item in raw):
            return [dict(item) for item in raw]
    return [{"name": _table_name(table)} for table in _iter_tables(source, app)]


def _lower_declared_engines(source: dict[str, Any], app: Any) -> list[dict[str, Any]]:
    raw = source.get("engines")
    if raw is not None:
        if not (
            isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray))
        ):
            raise TypeError("rust runtime expects app.engines to be a sequence")
        if raw:
            return [
                dict(item)
                if isinstance(item, Mapping)
                else {"name": "default", "kind": str(item)}
                for item in raw
            ]

    engine = source.get("engine", getattr(app, "engine", None))
    if engine is None:
        return [{"name": "default", "kind": "inmemory", "language": "rust"}]

    try:
        from tigrbl_core._spec.engine_spec import EngineSpec

        spec = EngineSpec.from_any(engine)
    except Exception:
        spec = None

    kind = "inmemory"
    options: dict[str, Any] = {}
    if spec is not None and getattr(spec, "kind", None):
        if spec.kind == "sqlite" and getattr(spec, "memory", False):
            kind = "inmemory"
        else:
            kind = str(spec.kind)
        path = getattr(spec, "path", None)
        if isinstance(path, str) and path:
            options["path"] = path
        dsn = getattr(spec, "dsn", None)
        if isinstance(dsn, str) and dsn:
            options["dsn"] = dsn
        options["memory"] = bool(getattr(spec, "memory", False))

    return [{"name": "default", "kind": kind, "language": "rust", "options": options}]


def _callable_name(value: Any) -> str:
    module = getattr(value, "__module__", None)
    qualname = getattr(value, "__qualname__", getattr(value, "__name__", None))
    if module and qualname:
        return f"{module}.{qualname}"
    return str(value)


def _lower_callbacks(source: dict[str, Any]) -> list[dict[str, Any]]:
    raw = source.get("callbacks", ()) or ()
    if not (
        isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray))
    ):
        raise TypeError("rust runtime expects app.callbacks to be a sequence")
    payload: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, Mapping):
            payload.append(dict(item))
            continue
        payload.append(
            {
                "name": _callable_name(item),
                "kind": "callback",
                "language": "python",
            }
        )
    return payload


def build_rust_app_spec(app: Any) -> dict[str, Any]:
    source = _as_mapping(app)
    name = _machine_name(source, app)
    payload: dict[str, Any] = {
        "name": name,
        "title": str(source.get("title", name)).strip(),
        "version": str(source.get("version", "0.1.0")).strip(),
        "jsonrpc_prefix": str(source.get("jsonrpc_prefix", "/rpc")).strip() or "/rpc",
        "system_prefix": str(source.get("system_prefix", "/system")).strip()
        or "/system",
        "metadata": dict(source.get("metadata", {}) or {}),
        "runtime": dict(source.get("runtime", {}) or {}),
        "dependencies": source.get("dependencies", {}) or {},
        "security": source.get("security", {}) or {},
        "bindings": _lower_declared_bindings(source, app),
        "tables": _lower_declared_tables(source, app),
        "engines": _lower_declared_engines(source, app),
        "callbacks": _lower_callbacks(source),
    }
    if not payload["name"]:
        raise ValueError("rust runtime requires a non-empty app name")
    return payload


def coerce_rust_spec_dict(app: Any) -> dict[str, Any]:
    if isinstance(app, str):
        payload = json.loads(app)
        if not isinstance(payload, dict):
            raise TypeError("rust runtime expects a mapping or JSON object")
        return payload
    if isinstance(app, Mapping):
        return build_rust_app_spec(dict(app))
    return build_rust_app_spec(app)


def coerce_rust_spec_json(app: Any) -> str:
    return json.dumps(coerce_rust_spec_dict(app), sort_keys=True)


__all__ = [
    "build_rust_app_spec",
    "coerce_rust_spec_dict",
    "coerce_rust_spec_json",
]
