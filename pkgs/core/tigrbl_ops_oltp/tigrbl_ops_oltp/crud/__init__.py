"""CRUD surface exports with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS = {
    'create': 'ops',
    'read': 'ops',
    'update': 'ops',
    'replace': 'ops',
    'merge': 'ops',
    'delete': 'ops',
    'list': 'ops',
    'clear': 'ops',
    'count': 'ops',
    'exists': 'ops',
    'bulk_create': 'bulk',
    'bulk_update': 'bulk',
    'bulk_replace': 'bulk',
    'bulk_merge': 'bulk',
    'bulk_delete': 'bulk',
    'Body': 'params',
    'Header': 'params',
    'Param': 'params',
    'Path': 'params',
    'Query': 'params',
}

__all__ = list(_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    attr = getattr(module, name)
    globals()[name] = attr
    return attr
