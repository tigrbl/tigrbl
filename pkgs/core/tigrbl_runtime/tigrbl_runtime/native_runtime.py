from __future__ import annotations

from typing import Any

from tigrbl_native import clear_ffi_boundary_events, create_runtime, ffi_boundary_events


def build_native_runtime(app: Any):
    return create_runtime(app)


def native_boundary_events() -> list[dict[str, object]]:
    return ffi_boundary_events()


def clear_native_boundary_events() -> None:
    clear_ffi_boundary_events()
