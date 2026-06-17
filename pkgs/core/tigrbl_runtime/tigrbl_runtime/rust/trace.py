from __future__ import annotations

from .errors import warn_rust_deprecated

_PYTHON_FFI_EVENTS: list[dict[str, object]] = []


def ffi_boundary_events() -> list[dict[str, object]]:
    warn_rust_deprecated()
    return list(_PYTHON_FFI_EVENTS)


def clear_ffi_boundary_events() -> None:
    warn_rust_deprecated()
    _PYTHON_FFI_EVENTS.clear()


def record_python_ffi_event(event: str, **payload: object) -> None:
    _PYTHON_FFI_EVENTS.append({"event": event, **payload})


def rust_available() -> bool:
    warn_rust_deprecated()
    return False


def compiled_extension_available() -> bool:
    warn_rust_deprecated()
    return False
