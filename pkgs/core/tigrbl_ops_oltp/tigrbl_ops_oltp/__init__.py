"""OLTP operation implementations for Tigrbl."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .fallback import native_handlers_enabled
from .native_handlers import register_native_handler

_LAZY_EXPORTS = {
    "Body": "crud",
    "Header": "crud",
    "Param": "crud",
    "Path": "crud",
    "Query": "crud",
    "bulk_create": "crud",
    "bulk_delete": "crud",
    "bulk_merge": "crud",
    "bulk_replace": "crud",
    "bulk_update": "crud",
    "clear": "crud",
    "create": "crud",
    "delete": "crud",
    "list": "crud",
    "merge": "crud",
    "read": "crud",
    "replace": "crud",
    "update": "crud",
}

__all__ = [
    "Body",
    "Header",
    "Param",
    "Path",
    "Query",
    "bulk_create",
    "bulk_delete",
    "bulk_merge",
    "bulk_replace",
    "bulk_update",
    "clear",
    "create",
    "delete",
    "list",
    "merge",
    "native_handlers_enabled",
    "read",
    "register_native_handler",
    "replace",
    "update",
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
