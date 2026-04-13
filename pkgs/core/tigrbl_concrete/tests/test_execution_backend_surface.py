from __future__ import annotations

import pytest


pytest.importorskip("sqlalchemy")


def test_app_and_router_accept_execution_backend() -> None:
    from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
    from tigrbl_runtime.native_runtime import build_native_runtime

    app = TigrblApp(mount_system=False, execution_backend="rust")
    router = TigrblRouter(execution_backend="python")
    runtime = build_native_runtime(
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
    assert isinstance(app.native_trace(), list)
    assert isinstance(router.native_trace(), list)
    assert runtime.execute_rest(
        {
            "operation": "users.create",
            "transport": "rest",
            "path": "/users",
            "method": "POST",
            "body": {"id": "u1"},
        }
    )["status"] == 201
