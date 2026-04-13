from __future__ import annotations

from typing import Any

from tigrbl_native import compile_app, native_parity_snapshot, normalize_spec

from .native_plan import NativePlan


def build_native_kernel(app: Any) -> NativePlan:
    normalized = normalize_spec(app)
    compiled = compile_app(app)
    return NativePlan(
        description=str(compiled.get("description", "compiled native plan")),
        compiled_plan=compiled,
        backend="rust",
        normalized_spec=normalized,
        parity_snapshot=native_parity_snapshot(app),
        claimable=False,
    )


def normalize_native_spec(app: Any) -> str:
    return normalize_spec(app)


def build_native_parity_snapshot(app: Any) -> dict[str, object]:
    return native_parity_snapshot(app)
