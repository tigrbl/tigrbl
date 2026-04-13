from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .errors import NativeBindingsUnavailableError

_REGISTRY: dict[str, Callable[..., Any]] = {}

try:
    from . import _native
except Exception as exc:  # pragma: no cover - exercised when extension is not built.
    from . import _fallback as _native
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def _require_native():
    if _native is None:
        raise NativeBindingsUnavailableError(
            "tigrbl_native._native is unavailable; build the extension before using native callbacks."
        ) from _IMPORT_ERROR
    return _native


def registered_python_callbacks() -> dict[str, Callable[..., Any]]:
    return dict(_REGISTRY)


def register_python_callback(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    native = _require_native()
    return native.register_python_callback(name)


def register_python_atom(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    native = _require_native()
    return native.register_python_atom(name)


def register_python_hook(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    native = _require_native()
    return native.register_python_hook(name)


def register_python_handler(name: str, callback: Callable[..., Any]) -> str:
    _REGISTRY[name] = callback
    native = _require_native()
    return native.register_python_handler(name)


def register_python_engine(name: str, callback: Callable[..., Any] | None = None) -> str:
    if callback is not None:
        _REGISTRY[name] = callback
    native = _require_native()
    return native.register_python_engine(name)
