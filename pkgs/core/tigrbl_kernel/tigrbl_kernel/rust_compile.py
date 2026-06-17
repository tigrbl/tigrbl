from __future__ import annotations
from typing import Any

from .rust_plan import RustPlan
import warnings


def _raise_deprecated(action: str) -> None:
    warnings.warn(
        "tigrbl_kernel Rust planning is deprecated; kernel planning is Python-only.",
        DeprecationWarning,
        stacklevel=3,
    )
    raise RuntimeError(f"{action} is unavailable; Tigrbl kernel planning is Python-only.")


def build_rust_kernel(app: Any) -> RustPlan:
    del app
    _raise_deprecated("build_rust_kernel")


def normalize_rust_spec(app: Any) -> str:
    del app
    _raise_deprecated("normalize_rust_spec")
