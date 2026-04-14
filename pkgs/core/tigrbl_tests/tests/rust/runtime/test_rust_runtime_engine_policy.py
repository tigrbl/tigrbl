from __future__ import annotations

import pytest

from tigrbl_runtime import Runtime


def test_rust_runtime_rejects_python_engine_without_explicit_callback() -> None:
    handle = Runtime(executor_backend="rust").rust_handle(
        {
            "name": "engine-policy-demo",
            "engines": [{"name": "legacy", "kind": "sqlite", "language": "python"}],
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

    with pytest.raises(RuntimeError, match="python-backed engine missing callback"):
        handle.execute_rest(
            {
                "operation": "users.create",
                "transport": "rest",
                "path": "/users",
                "method": "POST",
                "body": {"id": "u1"},
            }
        )
