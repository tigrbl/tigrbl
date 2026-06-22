from __future__ import annotations

import importlib.util


import tigrbl_kernel
from tigrbl_kernel import Kernel


def test_rust_kernel_helpers_are_not_public_facade_exports() -> None:
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


def test_rust_kernel_modules_are_removed() -> None:
    for module_name in (
        "tigrbl_kernel.rust_compile",
        "tigrbl_kernel.rust_spec",
        "tigrbl_kernel.rust_plan",
    ):
        assert importlib.util.find_spec(module_name) is None


def test_kernel_rust_compilation_method_is_removed() -> None:
    assert not hasattr(Kernel(), "compile_rust_plan")
