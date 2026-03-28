from __future__ import annotations

from typing import Any

from tigrbl_native import compile_app, normalize_spec

from .native_plan import NativePlan


def build_native_kernel(app: Any) -> NativePlan:
    normalized = normalize_spec(app)
    return NativePlan(
        description=compile_app(app),
        backend="rust",
        normalized_spec=normalized,
    )


def normalize_native_spec(app: Any) -> str:
    return normalize_spec(app)
