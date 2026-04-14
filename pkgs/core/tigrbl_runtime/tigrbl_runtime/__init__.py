"""Public exports for ``tigrbl_runtime`` with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .native import (
    ExecutionBackend,
    NativeBackendConfig,
    NativeBindingsUnavailableError,
)

_LAZY_EXPORTS = {
    "NativeRuntimeHandleRef": "handle",
    "Runtime": "runtime",
    "RuntimeBase": "runtime",
}

_NATIVE_EXPORTS = {
    "NativeRuntimeHandle": "NativeRuntimeHandle",
    "clear_native_boundary_events": "clear_ffi_boundary_events",
    "compiled_extension_available": "compiled_extension_available",
    "native_available": "native_available",
    "native_boundary_events": "ffi_boundary_events",
    "transport_parity_trace": "native_transport_trace",
}

__all__ = [
    "ExecutionBackend",
    "NativeBackendConfig",
    "NativeBindingsUnavailableError",
    *_LAZY_EXPORTS,
    *_NATIVE_EXPORTS,
]


def __getattr__(name: str) -> Any:
    native_name = _NATIVE_EXPORTS.get(name)
    if native_name is not None:
        module = import_module(f"{__name__}.native")
        value = getattr(module, native_name)
        globals()[name] = value
        return value

    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
