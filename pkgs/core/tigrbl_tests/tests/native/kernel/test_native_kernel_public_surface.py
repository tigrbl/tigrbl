from __future__ import annotations

from tigrbl_kernel.native_compile import build_native_kernel, normalize_native_spec
from tigrbl_native import ExecutionBackend


def test_native_kernel_surface_exposes_backend_aware_plan_helpers() -> None:
    native_plan = build_native_kernel({"name": "kernel-demo"})

    assert ExecutionBackend.RUST.value == "rust"
    assert native_plan.backend == "rust"
    assert native_plan.description.startswith("compiled-spec:")
    assert normalize_native_spec({"name": "kernel-demo"}).startswith("{")
