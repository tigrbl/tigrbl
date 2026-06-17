from __future__ import annotations

import pytest

import tigrbl_kernel
from tigrbl_kernel.rust_compile import build_rust_kernel, normalize_rust_spec
from tigrbl_kernel.rust_plan import RustPlan
from tigrbl_kernel.rust_spec import (
    build_rust_app_spec,
    coerce_rust_spec_dict,
    coerce_rust_spec_json,
)


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


def test_rust_kernel_surface_retirement_t1_shims_fail_closed() -> None:
    for helper in (build_rust_kernel, normalize_rust_spec):
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RuntimeError, match="Python-only"):
                helper({"name": "kernel-demo"})

    for helper in (
        build_rust_app_spec,
        coerce_rust_spec_dict,
        coerce_rust_spec_json,
    ):
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RuntimeError, match="Python-only"):
                helper({"name": "kernel-demo"})

    with pytest.warns(DeprecationWarning):
        plan = RustPlan(description="deprecated compatibility shim")
    assert plan.backend == "deprecated-rust"
