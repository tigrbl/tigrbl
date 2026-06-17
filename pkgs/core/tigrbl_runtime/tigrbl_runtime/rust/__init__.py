from __future__ import annotations

from .backend import (
    ExecutionBackend,
    RustBackendConfig,
    coerce_execution_backend,
    reject_rust_backend,
    wants_rust_backend,
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
    build_rust_app_spec,
    coerce_rust_spec_dict,
    coerce_rust_spec_json,
)
from .compile import compile_app, normalize_spec
from .request import RustRequest
from .response import RustResponse
from .errors import RustBindingsUnavailableError, RustSupportDeprecatedError
from .runtime import (
    RustRuntimeHandle,
    create_runtime,
    create_runtime_from_compiled,
)
from .trace import (
    clear_ffi_boundary_events,
    compiled_extension_available,
    ffi_boundary_events,
    rust_available,
)

__all__ = [
    "ExecutionBackend",
    "RustBackendConfig",
    "RustBindingsUnavailableError",
    "RustSupportDeprecatedError",
    "RustRequest",
    "RustResponse",
    "RustRuntimeHandle",
    "build_rust_app_spec",
    "clear_ffi_boundary_events",
    "coerce_rust_spec_dict",
    "coerce_rust_spec_json",
    "coerce_execution_backend",
    "compile_app",
    "compiled_extension_available",
    "create_runtime",
    "create_runtime_from_compiled",
    "ffi_boundary_events",
    "rust_available",
    "normalize_spec",
    "register_python_atom",
    "register_python_callback",
    "register_python_engine",
    "register_python_handler",
    "register_python_hook",
    "registered_python_callbacks",
    "reject_rust_backend",
    "wants_rust_backend",
]
