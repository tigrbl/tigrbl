from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .errors import raise_rust_deprecated
from .trace import record_python_ffi_event

_REGISTRY: dict[str, Callable[..., Any]] = {}


def registered_python_callbacks() -> dict[str, Callable[..., Any]]:
    return dict(_REGISTRY)


def register_python_callback(name: str, callback: Callable[..., Any]) -> str:
    del callback
    record_python_ffi_event("rust_callback_deprecated", name=name)
    raise_rust_deprecated("tigrbl_runtime.rust.register_python_callback")


def register_python_atom(name: str, callback: Callable[..., Any]) -> str:
    del callback
    record_python_ffi_event("rust_atom_deprecated", name=name)
    raise_rust_deprecated("tigrbl_runtime.rust.register_python_atom")


def register_python_hook(name: str, callback: Callable[..., Any]) -> str:
    del callback
    record_python_ffi_event("rust_hook_deprecated", name=name)
    raise_rust_deprecated("tigrbl_runtime.rust.register_python_hook")


def register_python_handler(name: str, callback: Callable[..., Any]) -> str:
    del callback
    record_python_ffi_event("rust_handler_deprecated", name=name)
    raise_rust_deprecated("tigrbl_runtime.rust.register_python_handler")


def register_python_engine(name: str, callback: Callable[..., Any] | None = None) -> str:
    del callback
    record_python_ffi_event("rust_engine_deprecated", name=name)
    raise_rust_deprecated("tigrbl_runtime.rust.register_python_engine")
