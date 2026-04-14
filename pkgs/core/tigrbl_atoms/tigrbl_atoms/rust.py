from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from tigrbl_runtime.rust import (
        register_python_atom,
        register_python_callback,
        register_python_hook,
    )
except Exception:  # pragma: no cover - additive optional integration
    register_python_atom = None
    register_python_callback = None
    register_python_hook = None


def register_rust_callback(name: str, callback: Callable[..., Any]) -> str:
    if register_python_callback is None:
        return f"python-callback:{name}"
    return register_python_callback(name, callback)


def register_rust_atom(name: str, callback: Callable[..., Any]) -> str:
    if register_python_atom is None:
        return f"python-atom:{name}"
    return register_python_atom(name, callback)


def register_rust_hook(name: str, callback: Callable[..., Any]) -> str:
    if register_python_hook is None:
        return f"python-hook:{name}"
    return register_python_hook(name, callback)
