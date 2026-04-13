from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def _as_mapping(app: Any) -> dict[str, Any]:
    if isinstance(app, str):
        return json.loads(app)
    if isinstance(app, Mapping):
        return dict(app)
    payload: dict[str, Any] = {
        "name": getattr(app, "name", getattr(app, "TITLE", app.__class__.__name__)),
        "title": getattr(app, "title", getattr(app, "TITLE", app.__class__.__name__)),
        "version": getattr(app, "version", getattr(app, "VERSION", "0.1.0")),
        "jsonrpc_prefix": getattr(app, "jsonrpc_prefix", "/rpc"),
        "system_prefix": getattr(app, "system_prefix", "/system"),
        "bindings": list(getattr(app, "bindings", []) or []),
        "tables": list(getattr(app, "tables", []) or []),
        "engines": list(getattr(app, "engines", []) or []),
        "callbacks": list(getattr(app, "callbacks", []) or []),
        "runtime": dict(getattr(app, "runtime_config", {}) or {}),
        "metadata": dict(getattr(app, "metadata", {}) or {}),
    }
    return payload


def build_startup_payload(app: Any) -> dict[str, Any]:
    source = _as_mapping(app)
    payload: dict[str, Any] = {
        "name": str(source.get("name", "")).strip(),
        "title": str(source.get("title", source.get("name", ""))).strip(),
        "version": str(source.get("version", "0.1.0")).strip(),
        "jsonrpc_prefix": str(source.get("jsonrpc_prefix", "/rpc")).strip() or "/rpc",
        "system_prefix": str(source.get("system_prefix", "/system")).strip() or "/system",
        "metadata": dict(source.get("metadata", {}) or {}),
        "runtime": dict(source.get("runtime", {}) or {}),
        "dependencies": source.get("dependencies", {}) or {},
        "security": source.get("security", {}) or {},
        "bindings": list(source.get("bindings", []) or []),
        "tables": list(source.get("tables", []) or []),
        "engines": list(source.get("engines", []) or []),
        "callbacks": list(source.get("callbacks", []) or []),
    }
    if not payload["name"]:
        raise ValueError("startup payload requires a non-empty app name")
    return payload
