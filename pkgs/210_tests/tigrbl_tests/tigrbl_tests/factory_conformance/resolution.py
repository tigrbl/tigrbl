from __future__ import annotations

from importlib import import_module
from typing import Any


def resolve_symbol(path: str) -> Any:
    module_name, separator, qualname = path.partition(":")
    if not separator or not module_name or not qualname:
        raise ValueError(f"symbol path must use module:qualname form: {path!r}")
    value: Any = import_module(module_name)
    for component in qualname.split("."):
        value = getattr(value, component)
    return value
