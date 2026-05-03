from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module
from .trace import record_python_ffi_event

_REGISTRY: dict[str, Callable[..., Any]] = {}

_rust, _IMPORT_ERROR = load_rust_module()


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension before using Rust callbacks."
        ) from _IMPORT_ERROR
    return _rust


def registered_python_callbacks() -> dict[str, Callable[..., Any]]:
    return dict(_REGISTRY)


def register_python_callback(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    record_python_ffi_event("register_python_callback", name=name)
    rust = _require_rust()
    return rust.register_python_callback(name)


def register_python_atom(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    record_python_ffi_event("register_python_atom", name=name)
    rust = _require_rust()
    return rust.register_python_atom(name)


def register_python_hook(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    record_python_ffi_event("register_python_hook", name=name)
    rust = _require_rust()
    return rust.register_python_hook(name)


def register_python_handler(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    record_python_ffi_event("register_python_handler", name=name)
    rust = _require_rust()
    return rust.register_python_handler(name)


def register_python_engine(name: str, callback: Callable[..., Any] | None = None) -> str:
    if callback is not None:
        _REGISTRY[name] = callback
    record_python_ffi_event("register_python_engine", name=name)
    rust = _require_rust()
    return rust.register_python_engine(name)
