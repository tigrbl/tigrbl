"""Public exports for ``tigrbl_typing`` with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_LAZY_EXPORTS = {
    'PgUUID': 'types',
}

__all__ = list(_LAZY_EXPORTS)


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
