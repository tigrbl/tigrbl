from __future__ import annotations

from .backend import (
    ExecutionBackend,
    NativeBackendConfig,
    coerce_execution_backend,
    wants_native_backend,
)
from .callbacks import (
    register_python_atom,
    register_python_callback,
    register_python_engine,
    register_python_handler,
    register_python_hook,
    registered_python_callbacks,
)
from .codec import (
    build_native_app_spec,
    coerce_native_spec_dict,
    coerce_native_spec_json,
)
from .compile import compile_app, normalize_spec
from .parity import (
    native_parity_snapshot,
    native_transport_trace,
    reference_parity_snapshot,
    reference_transport_trace,
)
from .request import NativeRequest
from .response import NativeResponse
from .errors import NativeBindingsUnavailableError
from .runtime import (
    NativeRuntimeHandle,
    create_runtime,
    create_runtime_from_compiled,
)
from .trace import (
    clear_ffi_boundary_events,
    compiled_extension_available,
    ffi_boundary_events,
    native_available,
)

__all__ = [
    "ExecutionBackend",
    "NativeBackendConfig",
    "NativeBindingsUnavailableError",
    "NativeRequest",
    "NativeResponse",
    "NativeRuntimeHandle",
    "build_native_app_spec",
    "clear_ffi_boundary_events",
    "coerce_native_spec_dict",
    "coerce_native_spec_json",
    "coerce_execution_backend",
    "compile_app",
    "compiled_extension_available",
    "create_runtime",
    "create_runtime_from_compiled",
    "ffi_boundary_events",
    "native_available",
    "native_parity_snapshot",
    "native_transport_trace",
    "normalize_spec",
    "register_python_atom",
    "register_python_callback",
    "register_python_engine",
    "register_python_handler",
    "register_python_hook",
    "registered_python_callbacks",
    "reference_parity_snapshot",
    "reference_transport_trace",
    "wants_native_backend",
]
