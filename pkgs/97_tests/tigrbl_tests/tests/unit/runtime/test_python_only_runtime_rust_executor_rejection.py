from __future__ import annotations

import importlib.util

import pytest

from tigrbl_concrete._concrete import TigrblApp, TigrblRouter
from tigrbl_runtime import Runtime


def test_runtime_rust_backend_module_is_removed() -> None:
    assert importlib.util.find_spec("tigrbl_runtime.rust") is None


def test_runtime_rejects_unknown_backend_selector() -> None:
    selectors = (
        {"executor_backend": "native"},
        {"kernel_backend": "native"},
        {"atoms_backend": "native"},
    )

    for kwargs in selectors:
        with pytest.raises(ValueError, match="unsupported execution backend"):
            Runtime(**kwargs)


def test_concrete_app_and_router_reject_unknown_execution_backend() -> None:
    with pytest.raises(ValueError, match="unsupported execution backend"):
        TigrblApp(mount_system=False, execution_backend="native")

    with pytest.raises(ValueError, match="unsupported execution backend"):
        TigrblRouter(execution_backend="native")
