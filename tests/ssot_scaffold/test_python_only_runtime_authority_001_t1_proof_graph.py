from __future__ import annotations

import pytest

import tigrbl_runtime
from tigrbl_runtime import Runtime
from tigrbl_runtime.rust import (
    ExecutionBackend,
    RustBackendConfig,
    RustBindingsUnavailableError,
)


def test_python_only_runtime_authority_t1_backend_selection() -> None:
    assert set(tigrbl_runtime.__all__) == {"Runtime", "RuntimeBase"}
    assert not hasattr(tigrbl_runtime, "ExecutionBackend")
    assert not hasattr(tigrbl_runtime, "RustBackendConfig")

    python_runtime = Runtime(executor_backend="python")
    auto_runtime = Runtime(executor_backend=ExecutionBackend.AUTO)

    assert python_runtime.executor_backend is ExecutionBackend.PYTHON
    assert auto_runtime.executor_backend is ExecutionBackend.AUTO

    for kwargs in (
        {"executor_backend": "rust"},
        {"kernel_backend": "rust"},
        {"atoms_backend": "rust"},
        {"rust_backend": RustBackendConfig(backend=ExecutionBackend.RUST)},
    ):
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
                Runtime(**kwargs)
