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
    assert runtime.executor_backend == "python"


def test_app_router_and_runtime_reject_unknown_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
    from tigrbl_runtime import Runtime

    with pytest.raises(ValueError, match="unsupported execution backend"):
        TigrblApp(mount_system=False, execution_backend="native")
    with pytest.raises(ValueError, match="unsupported execution backend"):
        TigrblRouter(execution_backend="native")
    with pytest.raises(ValueError, match="unsupported execution backend"):
        Runtime(executor_backend="native")
