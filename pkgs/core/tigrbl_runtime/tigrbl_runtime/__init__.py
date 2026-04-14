"""Public exports for ``tigrbl_runtime`` with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

from .rust import (
    ExecutionBackend,
    RustBackendConfig,
    RustBindingsUnavailableError,
)

_LAZY_EXPORTS = {
    "RustRuntimeHandleRef": "handle",
    "Runtime": "runtime",
    "RuntimeBase": "runtime",
}

_RUST_EXPORTS = {
    "RustRuntimeHandle": "RustRuntimeHandle",
    "clear_rust_boundary_events": "clear_ffi_boundary_events",
    "compiled_extension_available": "compiled_extension_available",
    "rust_available": "rust_available",
    "rust_boundary_events": "ffi_boundary_events",
    "rust_transport_trace": "rust_transport_trace",
}

__all__ = [
    "ExecutionBackend",
    "RustBackendConfig",
    "RustBindingsUnavailableError",
    *_LAZY_EXPORTS,
    *_RUST_EXPORTS,
]


def __getattr__(name: str) -> Any:
    rust_name = _RUST_EXPORTS.get(name)
    if rust_name is not None:
        module = import_module(f"{__name__}.rust")
        value = getattr(module, rust_name)
        globals()[name] = value
        return value

    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
