from __future__ import annotations

import warnings
from typing import Any, NoReturn


def _raise_deprecated(action: str) -> NoReturn:
    warnings.warn(
        "tigrbl_kernel Rust spec serialization is deprecated; "
        "Tigrbl runtime execution is Python-only.",
        DeprecationWarning,
        stacklevel=3,
    )
    raise RuntimeError(f"{action} is unavailable; Tigrbl runtime execution is Python-only.")


def build_rust_app_spec(app: Any) -> dict[str, Any]:
    del app
    _raise_deprecated("build_rust_app_spec")


def coerce_rust_spec_dict(app: Any) -> dict[str, Any]:
    del app
    _raise_deprecated("coerce_rust_spec_dict")


def coerce_rust_spec_json(app: Any) -> str:
    del app
    _raise_deprecated("coerce_rust_spec_json")


__all__ = [
    "build_rust_app_spec",
    "coerce_rust_spec_dict",
    "coerce_rust_spec_json",
]
