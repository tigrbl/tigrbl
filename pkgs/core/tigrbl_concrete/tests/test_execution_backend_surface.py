from __future__ import annotations

import pytest


pytest.importorskip("sqlalchemy")


def test_app_and_router_accept_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter

    app = TigrblApp(mount_system=False, execution_backend="rust")
    router = TigrblRouter(execution_backend="python")

    assert app.execution_backend == "rust"
    assert router.execution_backend == "python"
    assert isinstance(app.native_trace(), list)
    assert isinstance(router.native_trace(), list)
