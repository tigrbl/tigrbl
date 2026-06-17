from __future__ import annotations

from typing import Any

from .errors import raise_rust_deprecated, warn_rust_deprecated

_BOUNDARY_EVENTS: list[dict[str, Any]] = []


def ffi_boundary_events() -> list[dict[str, Any]]:
    warn_rust_deprecated()
    return [dict(item) for item in _BOUNDARY_EVENTS]


def clear_ffi_boundary_events() -> None:
    warn_rust_deprecated()
    _BOUNDARY_EVENTS.clear()


def rust_available() -> bool:
    warn_rust_deprecated()
    return False


def compiled_extension_available() -> bool:
    warn_rust_deprecated()
    return False


def normalize_spec(spec_json: str) -> str:
    del spec_json
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.normalize_spec")


def compile_spec(spec_json: str) -> str:
    del spec_json
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.compile_spec")


class RuntimeHandle:
    def __init__(self, plan_json_payload: str) -> None:
        del plan_json_payload
        raise_rust_deprecated("tigrbl_runtime.rust._fallback.RuntimeHandle")


def create_runtime_handle(plan_json: str) -> RuntimeHandle:
    del plan_json
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.create_runtime_handle")


def register_python_callback(name: str, *_args: Any, **_kwargs: Any) -> str:
    del name
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.register_python_callback")


def register_python_atom(name: str, *_args: Any, **_kwargs: Any) -> str:
    del name
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.register_python_atom")


def register_python_hook(name: str, *_args: Any, **_kwargs: Any) -> str:
    del name
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.register_python_hook")


def register_python_handler(name: str, *_args: Any, **_kwargs: Any) -> str:
    del name
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.register_python_handler")


def register_python_engine(name: str, *_args: Any, **_kwargs: Any) -> str:
    del name
    raise_rust_deprecated("tigrbl_runtime.rust._fallback.register_python_engine")
