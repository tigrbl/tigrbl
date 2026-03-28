from __future__ import annotations

from .handle import NativeRuntimeHandleRef
from .native_runtime import (
    build_native_runtime,
    clear_native_boundary_events,
    native_boundary_events,
)

try:  # pragma: no cover - additive optional integration
    from tigrbl_native import ExecutionBackend, NativeBackendConfig
except Exception:  # pragma: no cover
    ExecutionBackend = NativeBackendConfig = None

__all__ = [
    "ExecutionBackend",
    "NativeBackendConfig",
    "NativeRuntimeHandleRef",
    "build_native_runtime",
    "clear_native_boundary_events",
    "native_boundary_events",
]
