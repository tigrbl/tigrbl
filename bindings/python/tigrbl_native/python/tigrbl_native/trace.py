from __future__ import annotations

import json

from .errors import NativeBindingsUnavailableError

try:
    from . import _native
except Exception as exc:  # pragma: no cover
    from . import _fallback as _native
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


def _require_native():
    if _native is None:
        raise NativeBindingsUnavailableError(
            "tigrbl_native._native is unavailable; build the extension or use the source fallback."
        ) from _IMPORT_ERROR
    return _native


def ffi_boundary_events() -> list[dict[str, object]]:
    native = _require_native()
    if hasattr(native, "ffi_boundary_events"):
        events = native.ffi_boundary_events()
        if isinstance(events, str):
            return list(json.loads(events))
        return list(events)
    return []


def clear_ffi_boundary_events() -> None:
    native = _require_native()
    if hasattr(native, "clear_ffi_boundary_events"):
        native.clear_ffi_boundary_events()


def native_available() -> bool:
    try:
        native = _require_native()
    except Exception:
        return False
    checker = getattr(native, "native_available", None)
    if callable(checker):
        return bool(checker())
    return True


def compiled_extension_available() -> bool:
    try:
        native = _require_native()
    except Exception:
        return False
    checker = getattr(native, "compiled_extension_available", None)
    if callable(checker):
        return bool(checker())
    module_file = getattr(native, "__file__", "")
    return str(module_file).endswith((".so", ".pyd", ".dylib"))
