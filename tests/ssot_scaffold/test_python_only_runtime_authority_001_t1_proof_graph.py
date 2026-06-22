from __future__ import annotations

import importlib.util

import pytest

import tigrbl_runtime
from tigrbl_runtime import Runtime


def test_python_only_runtime_authority_t1_backend_selection() -> None:
    assert set(tigrbl_runtime.__all__) == {"Runtime", "RuntimeBase"}
    assert not hasattr(tigrbl_runtime, "ExecutionBackend")
    assert not hasattr(tigrbl_runtime, "RustBackendConfig")
    assert importlib.util.find_spec("tigrbl_runtime.rust") is None

    python_runtime = Runtime(executor_backend="python")
    auto_runtime = Runtime(executor_backend="auto")

    assert python_runtime.executor_backend == "python"
    assert auto_runtime.executor_backend == "auto"

    for kwargs in (
        {"executor_backend": "native"},
        {"kernel_backend": "native"},
        {"atoms_backend": "native"},
    ):
        with pytest.raises(ValueError, match="unsupported execution backend"):
            Runtime(**kwargs)
