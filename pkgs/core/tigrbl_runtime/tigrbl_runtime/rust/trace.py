from __future__ import annotations

import json

from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module

_rust, _IMPORT_ERROR = load_rust_module()
_PYTHON_FFI_EVENTS: list[dict[str, object]] = []


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension or use the source fallback."
        ) from _IMPORT_ERROR
    return _rust


def ffi_boundary_events() -> list[dict[str, object]]:
    events: list[dict[str, object]] = list(_PYTHON_FFI_EVENTS)
    rust = _require_rust()
    if hasattr(rust, "ffi_boundary_events"):
        rust_events = rust.ffi_boundary_events()
        if isinstance(rust_events, str):
            events.extend(list(json.loads(rust_events)))
            return events
        events.extend(list(rust_events))
        return events
    return events


def clear_ffi_boundary_events() -> None:
    _PYTHON_FFI_EVENTS.clear()
    rust = _require_rust()
    if hasattr(rust, "clear_ffi_boundary_events"):
        rust.clear_ffi_boundary_events()


def record_python_ffi_event(event: str, **payload: object) -> None:
    _PYTHON_FFI_EVENTS.append({"event": event, **payload})


def rust_available() -> bool:
    try:
        rust = _require_rust()
    except Exception:
        return False
    checker = getattr(rust, "rust_available", None)
    if callable(checker):
        return bool(checker())
    return True


def compiled_extension_available() -> bool:
    try:
        rust = _require_rust()
    except Exception:
        return False
    checker = getattr(rust, "compiled_extension_available", None)
    if callable(checker):
        return bool(checker())
    module_file = getattr(rust, "__file__", "")
    return str(module_file).endswith((".so", ".pyd", ".dylib"))
