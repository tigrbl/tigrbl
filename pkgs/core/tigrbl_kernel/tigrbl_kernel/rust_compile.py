from __future__ import annotations
from typing import Any

from tigrbl_runtime.rust import compile_app, rust_parity_snapshot, normalize_spec
from tigrbl_runtime.rust.codec import build_rust_app_spec

from .rust_plan import RustPlan


def build_rust_kernel(app: Any) -> RustPlan:
    payload = build_rust_app_spec(app)
    normalized = normalize_spec(payload)
    compiled = compile_app(payload)
    return RustPlan(
        description=f"compiled rust KernelPlan for {compiled.get('app_name', payload['name'])}",
        compiled_plan=compiled,
        backend="rust",
        normalized_spec=normalized,
        parity_snapshot=rust_parity_snapshot(payload),
        claimable=False,
    )


def normalize_rust_spec(app: Any) -> str:
    return normalize_spec(build_rust_app_spec(app))


def build_rust_parity_snapshot(app: Any) -> dict[str, object]:
    return rust_parity_snapshot(build_rust_app_spec(app))
