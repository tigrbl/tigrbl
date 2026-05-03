from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any


def _resolve_runtime_hook(name: str) -> Callable[..., Any] | None:
    try:
        rust = import_module("tigrbl_runtime.rust")
    except Exception:  # pragma: no cover - additive optional integration
        return None
    candidate = getattr(rust, name, None)
    return candidate if callable(candidate) else None


def register_rust_callback(name: str, callback: Callable[..., Any]) -> str:
    register_python_callback = _resolve_runtime_hook("register_python_callback")
    if register_python_callback is None:
        return f"python-callback:{name}"
    return register_python_callback(name, callback)


def register_rust_atom(name: str, callback: Callable[..., Any]) -> str:
    register_python_atom = _resolve_runtime_hook("register_python_atom")
    if register_python_atom is None:
        return f"python-atom:{name}"
    return register_python_atom(name, callback)


def register_rust_hook(name: str, callback: Callable[..., Any]) -> str:
    register_python_hook = _resolve_runtime_hook("register_python_hook")
    if register_python_hook is None:
        return f"python-hook:{name}"
    return register_python_hook(name, callback)
