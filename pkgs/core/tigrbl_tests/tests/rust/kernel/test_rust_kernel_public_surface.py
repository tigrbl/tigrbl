from __future__ import annotations

from tigrbl_kernel.rust_compile import (
    build_rust_kernel,
    normalize_rust_spec,
)
from tigrbl_runtime import ExecutionBackend


def test_rust_kernel_surface_exposes_backend_aware_plan_helpers() -> None:
    rust_plan = build_rust_kernel({"name": "kernel-demo"})

    assert ExecutionBackend.RUST.value == "rust"
    assert rust_plan.backend == "rust"
    assert rust_plan.description.startswith("compiled rust KernelPlan")
    assert rust_plan.compiled_plan is not None
    assert rust_plan.compiled_plan["app_name"] == "kernel-demo"
    assert normalize_rust_spec({"name": "kernel-demo"}).startswith("{")
