"""Public exports for ``tigrbl_runtime`` with lazy loading."""

from __future__ import annotations

from importlib import import_module
from typing import Any

try:  # pragma: no cover - additive optional integration
    from tigrbl_native import ExecutionBackend, NativeBackendConfig
except Exception:  # pragma: no cover
    ExecutionBackend = NativeBackendConfig = None

_LAZY_EXPORTS = {
    'NativeRuntimeHandleRef': 'handle',
    'build_native_runtime': 'native_runtime',
    'clear_native_boundary_events': 'native_runtime',
    'native_boundary_events': 'native_runtime',
}

__all__ = [
    'ExecutionBackend',
    'NativeBackendConfig',
    *_LAZY_EXPORTS,
]


def __getattr__(name: str) -> Any:
    module_name = _LAZY_EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, name)
    globals()[name] = value
    return value
