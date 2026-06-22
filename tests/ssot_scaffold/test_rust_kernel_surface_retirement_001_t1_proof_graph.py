from __future__ import annotations

import importlib.util

import tigrbl_kernel


def test_rust_kernel_surface_retirement_t1_public_facade() -> None:
    blocked = {
        "ExecutionBackend",
        "RustBackendConfig",
        "RustPlan",
        "build_rust_kernel",
        "normalize_rust_spec",
    }
    assert blocked.isdisjoint(tigrbl_kernel.__all__)
    for name in blocked:
        assert not hasattr(tigrbl_kernel, name)


def test_rust_kernel_surface_retirement_t1_shims_are_removed() -> None:
    for module_name in (
        "tigrbl_kernel.rust_compile",
        "tigrbl_kernel.rust_plan",
        "tigrbl_kernel.rust_spec",
    ):
        assert importlib.util.find_spec(module_name) is None
    assert not hasattr(tigrbl_kernel.Kernel(), "compile_rust_plan")
