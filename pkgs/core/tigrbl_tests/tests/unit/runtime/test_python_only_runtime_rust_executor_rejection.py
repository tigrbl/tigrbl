from __future__ import annotations

import pytest

from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
from tigrbl_runtime import Runtime
from tigrbl_runtime.rust import (
    ExecutionBackend,
    RustBackendConfig,
    RustBindingsUnavailableError,
    reject_rust_backend,
)


def test_runtime_rejects_every_rust_backend_selector() -> None:
    selectors = (
        {"executor_backend": "rust"},
        {"executor_backend": ExecutionBackend.RUST},
        {"kernel_backend": "rust"},
        {"atoms_backend": "rust"},
        {"rust_backend": RustBackendConfig(backend=ExecutionBackend.RUST)},
        {"rust_backend": RustBackendConfig(strict_rust=True)},
    )

    for kwargs in selectors:
        with pytest.warns(DeprecationWarning):
            with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
                Runtime(**kwargs)


def test_reject_rust_backend_helper_fails_closed() -> None:
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            reject_rust_backend("rust", label="executor_backend")

    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            reject_rust_backend(ExecutionBackend.RUST, label="executor_backend")


def test_concrete_app_and_router_reject_rust_execution_backend() -> None:
    with pytest.raises(ValueError, match="Python-only"):
        TigrblApp(mount_system=False, execution_backend="rust")

    with pytest.raises(ValueError, match="Python-only"):
        TigrblRouter(execution_backend="rust")
