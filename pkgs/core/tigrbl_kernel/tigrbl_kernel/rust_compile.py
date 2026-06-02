from __future__ import annotations
from importlib import import_module
from typing import Any

from .rust_plan import RustPlan
from .rust_spec import build_rust_app_spec


def _runtime_rust_helpers():
    rust = import_module("tigrbl_runtime.rust")
    return (
        rust.compile_app,
        rust.normalize_spec,
    )


def build_rust_kernel(app: Any) -> RustPlan:
    compile_app, normalize_spec = _runtime_rust_helpers()
    payload = build_rust_app_spec(app)
    normalized = normalize_spec(payload)
    compiled = compile_app(payload)
    return RustPlan(
        description=f"compiled rust KernelPlan for {compiled.get('app_name', payload['name'])}",
        compiled_plan=compiled,
        backend="rust",
        normalized_spec=normalized,
    )


def normalize_rust_spec(app: Any) -> str:
    _, normalize_spec = _runtime_rust_helpers()
    return normalize_spec(build_rust_app_spec(app))
