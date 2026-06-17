from __future__ import annotations

import pytest

from tigrbl_kernel.rust_compile import build_rust_kernel, normalize_rust_spec
from tigrbl_runtime import ExecutionBackend


def test_rust_kernel_plan_helpers_are_deprecated() -> None:
    assert ExecutionBackend.RUST.value == "rust"

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            build_rust_kernel({"name": "kernel-demo"})
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RuntimeError, match="Python-only"):
            normalize_rust_spec({"name": "kernel-demo"})
