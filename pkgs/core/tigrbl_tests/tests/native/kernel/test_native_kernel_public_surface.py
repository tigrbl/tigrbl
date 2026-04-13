from __future__ import annotations

from tigrbl_kernel.native_compile import (
    build_native_kernel,
    build_native_parity_snapshot,
    normalize_native_spec,
)
from tigrbl_native import ExecutionBackend


def test_native_kernel_surface_exposes_backend_aware_plan_helpers() -> None:
    native_plan = build_native_kernel({"name": "kernel-demo"})

    assert ExecutionBackend.RUST.value == "rust"
    assert native_plan.backend == "rust"
    assert native_plan.description.startswith("compiled native KernelPlan")
    assert native_plan.compiled_plan is not None
    assert native_plan.compiled_plan["app_name"] == "kernel-demo"
    assert native_plan.parity_snapshot == build_native_parity_snapshot({"name": "kernel-demo"})
    assert native_plan.claimable is False
    assert normalize_native_spec({"name": "kernel-demo"}).startswith("{")
