from __future__ import annotations

import pytest


pytest.importorskip("sqlalchemy")


def test_app_and_router_accept_python_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
    from tigrbl_runtime import Runtime

    app = TigrblApp(mount_system=False, execution_backend="python")
    router = TigrblRouter(execution_backend="python")
    runtime = Runtime(executor_backend="python")

    assert app.execution_backend == "python"
    assert router.execution_backend == "python"
    assert runtime.executor_backend.value == "python"


def test_app_router_and_runtime_reject_rust_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
    from tigrbl_runtime import Runtime, RustBindingsUnavailableError

    with pytest.raises(ValueError, match="Python-only"):
        TigrblApp(mount_system=False, execution_backend="rust")
    with pytest.raises(ValueError, match="Python-only"):
        TigrblRouter(execution_backend="rust")
    with pytest.warns(DeprecationWarning):
        with pytest.raises(RustBindingsUnavailableError, match="Python-only"):
            Runtime(executor_backend="rust")
