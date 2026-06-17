from __future__ import annotations

from typing import Any

from .errors import raise_rust_deprecated


def normalize_spec(spec: Any) -> str:
    del spec
    raise_rust_deprecated("tigrbl_runtime.rust.normalize_spec")


def compile_app(spec: Any) -> dict[str, Any]:
    del spec
    raise_rust_deprecated("tigrbl_runtime.rust.compile_app")
