from __future__ import annotations
from importlib import import_module
from typing import Any

from .rust_plan import RustPlan


def _runtime_rust_helpers():
    rust = import_module("tigrbl_runtime.rust")
    codec = import_module("tigrbl_runtime.rust.codec")
    return (
        rust.compile_app,
        rust.rust_parity_snapshot,
        rust.normalize_spec,
        codec.build_rust_app_spec,
    )


def build_rust_kernel(app: Any) -> RustPlan:
    compile_app, rust_parity_snapshot, normalize_spec, build_rust_app_spec = (
        _runtime_rust_helpers()
    )
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
    _, _, normalize_spec, build_rust_app_spec = _runtime_rust_helpers()
    return normalize_spec(build_rust_app_spec(app))


def build_rust_parity_snapshot(app: Any) -> dict[str, object]:
    _, rust_parity_snapshot, _, build_rust_app_spec = _runtime_rust_helpers()
    return rust_parity_snapshot(build_rust_app_spec(app))
