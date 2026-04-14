from __future__ import annotations
from typing import Any

from tigrbl_runtime.native import compile_app, native_parity_snapshot, normalize_spec
from tigrbl_runtime.native.codec import build_native_app_spec

from .native_plan import NativePlan


def build_native_kernel(app: Any) -> NativePlan:
    payload = build_native_app_spec(app)
    normalized = normalize_spec(payload)
    compiled = compile_app(payload)
    return NativePlan(
        description=f"compiled native KernelPlan for {compiled.get('app_name', payload['name'])}",
        compiled_plan=compiled,
        backend="rust",
        normalized_spec=normalized,
        parity_snapshot=native_parity_snapshot(payload),
        claimable=False,
    )


def normalize_native_spec(app: Any) -> str:
    return normalize_spec(build_native_app_spec(app))


def build_native_parity_snapshot(app: Any) -> dict[str, object]:
    return native_parity_snapshot(build_native_app_spec(app))
