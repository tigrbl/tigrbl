from __future__ import annotations

import importlib

import pytest

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


def test_rust_kernel_modules_are_deprecated_fail_closed_shims() -> None:
    rust_compile = importlib.import_module("tigrbl_kernel.rust_compile")
    rust_spec = importlib.import_module("tigrbl_kernel.rust_spec")
    rust_plan = importlib.import_module("tigrbl_kernel.rust_plan")

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            rust_compile.build_rust_kernel({"name": "demo"})
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            rust_compile.normalize_rust_spec({"name": "demo"})

    for helper_name in (
        "build_rust_app_spec",
        "coerce_rust_spec_dict",
        "coerce_rust_spec_json",
    ):
        helper = getattr(rust_spec, helper_name)
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RuntimeError, match="Python-only"):
                helper({"name": "demo"})

    with pytest.warns(DeprecationWarning):
        plan = rust_plan.RustPlan(description="legacy shim")
    assert plan.backend == "deprecated-rust"


def test_kernel_rust_compilation_method_fails_closed() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            Kernel().compile_rust_plan({"name": "demo"})
