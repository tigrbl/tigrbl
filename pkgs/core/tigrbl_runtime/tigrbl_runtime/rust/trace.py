from __future__ import annotations

import json

from .errors import RustBindingsUnavailableError
from ._load_rust import load_rust_module

_rust, _IMPORT_ERROR = load_rust_module()


def _require_rust():
    if _rust is None:
        raise RustBindingsUnavailableError(
            "tigrbl_runtime.rust._rust is unavailable; build the runtime extension or use the source fallback."
        ) from _IMPORT_ERROR
    return _rust


def ffi_boundary_events() -> list[dict[str, object]]:
    rust = _require_rust()
    if hasattr(rust, "ffi_boundary_events"):
        events = rust.ffi_boundary_events()
        if isinstance(events, str):
            return list(json.loads(events))
        return list(events)
    return []


def clear_ffi_boundary_events() -> None:
    rust = _require_rust()
    if hasattr(rust, "clear_ffi_boundary_events"):
        rust.clear_ffi_boundary_events()


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
