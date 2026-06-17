from __future__ import annotations

from typing import Any

from .errors import raise_rust_deprecated


def build_rust_app_spec(app: Any) -> dict[str, Any]:
    del app
    raise_rust_deprecated("tigrbl_runtime.rust.codec.build_rust_app_spec")


def coerce_rust_spec_dict(app: Any) -> dict[str, Any]:
    del app
    raise_rust_deprecated("tigrbl_runtime.rust.codec.coerce_rust_spec_dict")


def coerce_rust_spec_json(app: Any) -> str:
    del app
    raise_rust_deprecated("tigrbl_runtime.rust.codec.coerce_rust_spec_json")


__all__ = [
    "build_rust_app_spec",
    "coerce_rust_spec_dict",
    "coerce_rust_spec_json",
]
