from __future__ import annotations

from typing import Any


def normalize_execution_backend(value: Any) -> str:
    if value is None:
        return "auto"
    lowered = str(value).strip().lower()
    if lowered not in {"auto", "python", "rust"}:
        raise ValueError(f"unsupported execution backend: {value!r}")
    return lowered


def ffi_boundary_events() -> list[dict[str, Any]]:
    try:
        from tigrbl_runtime.native import ffi_boundary_events as _ffi_boundary_events
    except Exception:
        return []
    return list(_ffi_boundary_events())


def clear_ffi_boundary_events() -> None:
    try:
        from tigrbl_runtime.native import clear_ffi_boundary_events as _clear
    except Exception:
        return None
    _clear()
