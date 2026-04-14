from __future__ import annotations

import pytest


pytest.importorskip("sqlalchemy")


def test_app_and_router_accept_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
    from tigrbl_runtime import Runtime

    app = TigrblApp(mount_system=False, execution_backend="rust")
    router = TigrblRouter(execution_backend="python")
    runtime = Runtime(executor_backend="rust")
    handle = runtime.rust_handle(
        {
            "name": "demo",
            "bindings": [
                {
                    "alias": "users.create",
                    "transport": "rest",
                    "path": "/users",
                    "op": {"name": "create", "kind": "create", "route": "/users"},
                    "table": {"name": "users"},
                }
            ],
        }
    )

    assert app.execution_backend == "rust"
    assert router.execution_backend == "python"
    assert isinstance(app.rust_trace(), list)
    assert isinstance(router.rust_trace(), list)
    assert handle.execute_rest(
        {
            "operation": "users.create",
            "transport": "rest",
            "path": "/users",
            "method": "POST",
            "body": {"id": "u1"},
        }
    )["status"] == 201
